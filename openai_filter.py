import json
import csv
from pathlib import Path
from transformers import pipeline

# ─────────────────────────────────────────────
# 1. LOAD MODEL
# ─────────────────────────────────────────────

print("Loading OpenAI Privacy Filter...")
pii_pipeline = pipeline(
    "token-classification",
    model="openai/privacy-filter",
    aggregation_strategy="simple",
    trust_remote_code=True
)
print("Model loaded.\n")


# ─────────────────────────────────────────────
# 2. LABEL MAPPING
# ─────────────────────────────────────────────

LABEL_MAP = {
    "PRIVATE_EMAIL":   "EMAIL",
    "PRIVATE_PHONE":   "TEL",
    "PRIVATE_URL":     "URL",
    "PRIVATE_DATE":    "DATE",
    "PRIVATE_PERSON":  "GIVENNAME1",
    "PRIVATE_ADDRESS": "STREET",
    "ACCOUNT_NUMBER":  "SOCIALNUMBER",
    "SECRET":          "PASS",
}

def map_label(openai_label):
    # model outputs lowercase — uppercase before lookup
    return LABEL_MAP.get(openai_label.upper(), openai_label.upper())


# ─────────────────────────────────────────────
# 3. PREDICT FUNCTION
# ─────────────────────────────────────────────

def predict_openai(text):
    try:
        results = pii_pipeline(text)
        predictions = []
        for r in results:
            predictions.append({
                "value": r["word"],
                "start": r["start"],
                "end":   r["end"],
                "label": map_label(r["entity_group"])
            })
        return predictions
    except Exception as e:
        print(f"  [ERROR] prediction failed: {e}")
        return []


# ─────────────────────────────────────────────
# 4. EVALUATION
# Overlap-based matching:
# - prediction is TP if it overlaps any GT span of same label
# - each GT span can only be matched once
# - each pred span can only be matched once
# - unmatched predictions = FP
# - unmatched GT spans = FN
# Note: model splits some spans (e.g. email into user@domain + .com)
# causing inflated FP counts — documented as a known limitation
# ─────────────────────────────────────────────

def evaluate_sample(predictions, ground_truth):
    tp, fp, fn = 0, 0, 0
    per_label = {}
    matched_gt   = set()
    matched_pred = set()

    for pi, pred in enumerate(predictions):
        matched = False
        for gi, gt in enumerate(ground_truth):
            if (pred["label"] == gt["label"] and
                    pred["start"] < gt["end"] and
                    pred["end"]   > gt["start"]):
                if gi not in matched_gt:
                    tp += 1
                    matched_gt.add(gi)
                    matched_pred.add(pi)
                    matched = True
                    label = pred["label"]
                    if label not in per_label:
                        per_label[label] = {"tp": 0, "fp": 0, "fn": 0}
                    per_label[label]["tp"] += 1
                    break
        if not matched:
            fp += 1
            label = pred["label"]
            if label not in per_label:
                per_label[label] = {"tp": 0, "fp": 0, "fn": 0}
            per_label[label]["fp"] += 1

    for gi, gt in enumerate(ground_truth):
        if gi not in matched_gt:
            fn += 1
            label = gt["label"]
            if label not in per_label:
                per_label[label] = {"tp": 0, "fp": 0, "fn": 0}
            per_label[label]["fn"] += 1

    return tp, fp, fn, per_label


def compute_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    fnr       = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    fpr       = fp / (fp + tp) if (fp + tp) > 0 else 0.0
    return precision, recall, f1, fnr, fpr


# ─────────────────────────────────────────────
# 5. MAIN
# ─────────────────────────────────────────────

def main():
    sample_path = Path("sample.jsonl")
    if not sample_path.exists():
        print("ERROR: sample.jsonl not found. Run sampler.py first.")
        return

    print("Loading sample...")
    samples = []
    with open(sample_path, "r", encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))
    print(f"Loaded {len(samples)} samples.\n")

    total_tp, total_fp, total_fn = 0, 0, 0
    label_totals = {}
    lang_totals  = {}
    skipped      = 0
    rows         = []
    raw_labels_seen = set()

    for i, sample in enumerate(samples):
        if i % 100 == 0:
            print(f"  Processing {i}/{len(samples)}...")

        text         = sample["source_text"]
        ground_truth = sample["privacy_mask"]
        language     = sample["language"]
        sample_id    = sample["id"]

        if len(text) > 2000:
            skipped += 1
            continue

        predictions = predict_openai(text)

        for p in predictions:
            raw_labels_seen.add(p["label"])

        tp, fp, fn, per_label = evaluate_sample(predictions, ground_truth)

        total_tp += tp
        total_fp += fp
        total_fn += fn

        for label, counts in per_label.items():
            if label not in label_totals:
                label_totals[label] = {"tp": 0, "fp": 0, "fn": 0}
            for k in counts:
                label_totals[label][k] += counts[k]

        if language not in lang_totals:
            lang_totals[language] = {"tp": 0, "fp": 0, "fn": 0}
        lang_totals[language]["tp"] += tp
        lang_totals[language]["fp"] += fp
        lang_totals[language]["fn"] += fn

        p, r, f1, fnr, fpr = compute_metrics(tp, fp, fn)
        rows.append({
            "sample_id": sample_id,
            "language":  language,
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(p,  4),
            "recall":    round(r,  4),
            "f1":        round(f1, 4),
            "fnr":       round(fnr, 4),
            "fpr":       round(fpr, 4),
            "model":     "openai_privacy_filter"
        })

    print(f"\nRaw labels produced by OpenAI filter (after mapping): {sorted(raw_labels_seen)}")
    print(f"Skipped samples (too long): {skipped}")

    # ── Overall ──
    print("\n" + "="*50)
    print("OVERALL RESULTS — OpenAI Privacy Filter")
    print("="*50)
    p, r, f1, fnr, fpr = compute_metrics(total_tp, total_fp, total_fn)
    print(f"  TP: {total_tp}  FP: {total_fp}  FN: {total_fn}")
    print(f"  Precision : {p:.4f}")
    print(f"  Recall    : {r:.4f}")
    print(f"  F1        : {f1:.4f}")
    print(f"  FNR       : {fnr:.4f}")
    print(f"  FPR       : {fpr:.4f}")

    # ── Per-label ──
    print("\n" + "="*50)
    print("PER-LABEL BREAKDOWN")
    print("="*50)
    print(f"{'Label':<25} {'TP':>6} {'FP':>6} {'FN':>6} {'Precision':>10} {'Recall':>8} {'F1':>8} {'FNR':>8}")
    for label, counts in sorted(label_totals.items()):
        p, r, f1, fnr, fpr = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
        print(f"{label:<25} {counts['tp']:>6} {counts['fp']:>6} {counts['fn']:>6} {p:>10.4f} {r:>8.4f} {f1:>8.4f} {fnr:>8.4f}")

    # ── Per-language ──
    print("\n" + "="*50)
    print("PER-LANGUAGE BREAKDOWN")
    print("="*50)
    print(f"{'Language':<12} {'TP':>6} {'FP':>6} {'FN':>6} {'Precision':>10} {'Recall':>8} {'F1':>8} {'FNR':>8}")
    for lang, counts in sorted(lang_totals.items()):
        p, r, f1, fnr, fpr = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
        print(f"{lang:<12} {counts['tp']:>6} {counts['fp']:>6} {counts['fn']:>6} {p:>10.4f} {r:>8.4f} {f1:>8.4f} {fnr:>8.4f}")

    # ── Save CSV ──
    csv_path = "openai_results.csv"
    fieldnames = ["sample_id", "language", "tp", "fp", "fn",
                  "precision", "recall", "f1", "fnr", "fpr", "model"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"\nSaved per-sample results to {csv_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()