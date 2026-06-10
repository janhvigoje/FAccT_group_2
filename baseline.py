import json
import re
import csv
from pathlib import Path

# ─────────────────────────────────────────────
# 1. REGEX PATTERNS
# ─────────────────────────────────────────────

PATTERNS = {
    "EMAIL": re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    ),
    "PHONE": re.compile(
        r"(\+?[\d\s\-\(\)]{7,15}\d)"
    ),
    "URL": re.compile(
        r"https?://[^\s]+"
    ),
    "DATE": re.compile(
        r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b"
    ),
    "IBAN": re.compile(
        r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b"
    ),
}

# ─────────────────────────────────────────────
# 2. PREDICT FUNCTION
# ─────────────────────────────────────────────

def predict_regex(text):
    """Return list of {value, start, end, label} dicts for all regex matches."""
    predictions = []
    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            predictions.append({
                "value": match.group(),
                "start": match.start(),
                "end": match.end(),
                "label": label
            })
    return predictions


# ─────────────────────────────────────────────
# 3. EVALUATION FUNCTIONS
# ─────────────────────────────────────────────

def spans_overlap(pred_start, pred_end, gt_start, gt_end):
    """Check if two spans overlap at all."""
    return pred_start < gt_end and pred_end > gt_start


def evaluate_sample(predictions, ground_truth):
    """
    Evaluate predictions against ground truth spans.
    Uses exact label + exact span match for TP.
    Returns TP, FP, FN counts and per-label breakdown.
    """
    tp, fp, fn = 0, 0, 0
    per_label = {}  # label -> {tp, fp, fn}

    matched_gt = set()
    matched_pred = set()

    for pi, pred in enumerate(predictions):
        matched = False
        for gi, gt in enumerate(ground_truth):
            if (pred["label"] == gt["label"] and
                    pred["start"] == gt["start"] and
                    pred["end"] == gt["end"]):
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
    fpr       = fp / (fp + tp) if (fp + tp) > 0 else 0.0  # approximation
    return precision, recall, f1, fnr, fpr


# ─────────────────────────────────────────────
# 4. MAIN
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
    print(f"Loaded {len(samples)} samples.")

    # Aggregate counters
    total_tp, total_fp, total_fn = 0, 0, 0
    label_totals = {}   # label -> {tp, fp, fn}
    lang_totals  = {}   # language -> {tp, fp, fn}

    rows = []  # for CSV output

    for sample in samples:
        text       = sample["source_text"]
        ground_truth = sample["privacy_mask"]
        language   = sample["language"]
        sample_id  = sample["id"]

        # Only evaluate regex-detectable labels in ground truth
        # (filter GT to labels our regex covers)
        gt_filtered = [g for g in ground_truth if g["label"] in PATTERNS]

        predictions = predict_regex(text)

        tp, fp, fn, per_label = evaluate_sample(predictions, gt_filtered)

        total_tp += tp
        total_fp += fp
        total_fn += fn

        # Accumulate per-label
        for label, counts in per_label.items():
            if label not in label_totals:
                label_totals[label] = {"tp": 0, "fp": 0, "fn": 0}
            for k in counts:
                label_totals[label][k] += counts[k]

        # Accumulate per-language
        if language not in lang_totals:
            lang_totals[language] = {"tp": 0, "fp": 0, "fn": 0}
        lang_totals[language]["tp"] += tp
        lang_totals[language]["fp"] += fp
        lang_totals[language]["fn"] += fn

        # Row for CSV
        p, r, f1, fnr, fpr = compute_metrics(tp, fp, fn)
        rows.append({
            "sample_id": sample_id,
            "language": language,
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(p, 4),
            "recall": round(r, 4),
            "f1": round(f1, 4),
            "fnr": round(fnr, 4),
            "fpr": round(fpr, 4),
            "model": "regex_baseline"
        })

    # ── Print overall results ──
    print("\n" + "="*50)
    print("OVERALL RESULTS — Regex Baseline")
    print("="*50)
    p, r, f1, fnr, fpr = compute_metrics(total_tp, total_fp, total_fn)
    print(f"  TP: {total_tp}  FP: {total_fp}  FN: {total_fn}")
    print(f"  Precision : {p:.4f}")
    print(f"  Recall    : {r:.4f}")
    print(f"  F1        : {f1:.4f}")
    print(f"  FNR       : {fnr:.4f}")
    print(f"  FPR       : {fpr:.4f}")

    # ── Per-label breakdown ──
    print("\n" + "="*50)
    print("PER-LABEL BREAKDOWN")
    print("="*50)
    print(f"{'Label':<20} {'TP':>6} {'FP':>6} {'FN':>6} {'Precision':>10} {'Recall':>8} {'F1':>8} {'FNR':>8}")
    for label, counts in sorted(label_totals.items()):
        p, r, f1, fnr, fpr = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
        print(f"{label:<20} {counts['tp']:>6} {counts['fp']:>6} {counts['fn']:>6} {p:>10.4f} {r:>8.4f} {f1:>8.4f} {fnr:>8.4f}")

    # ── Per-language breakdown ──
    print("\n" + "="*50)
    print("PER-LANGUAGE BREAKDOWN")
    print("="*50)
    print(f"{'Language':<12} {'TP':>6} {'FP':>6} {'FN':>6} {'Precision':>10} {'Recall':>8} {'F1':>8} {'FNR':>8}")
    for lang, counts in sorted(lang_totals.items()):
        p, r, f1, fnr, fpr = compute_metrics(counts["tp"], counts["fp"], counts["fn"])
        print(f"{lang:<12} {counts['tp']:>6} {counts['fp']:>6} {counts['fn']:>6} {p:>10.4f} {r:>8.4f} {f1:>8.4f} {fnr:>8.4f}")

    # ── Save to CSV ──
    output_path = "baseline_results.csv"
    fieldnames = ["sample_id", "language", "tp", "fp", "fn",
                  "precision", "recall", "f1", "fnr", "fpr", "model"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved per-sample results to {output_path}")
    print("Done.")


if __name__ == "__main__":
    main()