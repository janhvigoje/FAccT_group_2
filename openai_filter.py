import json
import csv
from pathlib import Path
from collections import defaultdict
from transformers import pipeline


# ─────────────────────────────────────────────────────────────────────────────
# 1. LABEL TAXONOMY
# ─────────────────────────────────────────────────────────────────────────────

# All 29 ai4privacy dataset labels
DATASET_LABELS = {
    "EMAIL", "TEL", "IP", "URL",
    "GIVENNAME1", "GIVENNAME2", "LASTNAME1", "LASTNAME2", "MIDDLENAME",
    "USERNAME", "PASSWORD", "PASS",
    "STREET", "CITY", "STATE", "POSTCODE", "COUNTRY",
    "DATE", "TIME", "AGE",
    "SOCIALNUMBER", "IDCARD", "ACCOUNTNUMBER", "CREDITCARDNUMBER",
    "IBAN", "BITCOINADDRESS",
    "JOBTYPE", "COMPANY", "JOBTITLE",
    "SEX", "HEIGHT", "WEIGHT", "BLOODTYPE", "ETHNICITY",
    "VEHICLEIDENTIFICATIONNUMBER", "VEHICLEVRM",
    "CURRENCY", "AMOUNT",
    "USERAGENT", "MACADDRESS",
    "ORDINALDIRECTION", "COUNTY",
}

# Canonical internal label set used in evaluation (post-collapse)
CANONICAL_PERSON   = "PERSON"
CANONICAL_ADDRESS  = "ADDRESS"

# Groups of dataset labels that collapse into one canonical label
NAME_LABELS    = {"GIVENNAME1", "GIVENNAME2", "LASTNAME1", "LASTNAME2", "MIDDLENAME"}
ADDRESS_LABELS = {"STREET", "CITY", "STATE", "POSTCODE", "COUNTRY", "COUNTY",
                  "ORDINALDIRECTION"}

# Model output label → one or more canonical evaluation labels
# A prediction matches GT if its mapped label is in the target set
MODEL_TO_CANONICAL = {
    "PRIVATE_EMAIL":   {"EMAIL"},
    "PRIVATE_PHONE":   {"TEL"},
    "PRIVATE_URL":     {"URL", "IP"},          # model can't distinguish — credit both
    "PRIVATE_DATE":    {"DATE"},
    "PRIVATE_PERSON":  {CANONICAL_PERSON},
    "PRIVATE_ADDRESS": {CANONICAL_ADDRESS},
    "ACCOUNT_NUMBER":  {"SOCIALNUMBER", "ACCOUNTNUMBER", "IBAN",
                        "BITCOINADDRESS", "CREDITCARDNUMBER", "IDCARD"},
    "SECRET":          {"PASS", "PASSWORD"},
}

# Flat set of all canonical labels the model can detect (used for in-scope filter)
IN_SCOPE_CANONICAL = set()
for targets in MODEL_TO_CANONICAL.values():
    IN_SCOPE_CANONICAL.update(targets)
IN_SCOPE_CANONICAL.add(CANONICAL_PERSON)
IN_SCOPE_CANONICAL.add(CANONICAL_ADDRESS)


# ─────────────────────────────────────────────────────────────────────────────
# 2. LABEL MAPPING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def collapse_dataset_label(label: str) -> str:
    """
    Collapse fine-grained dataset labels into canonical evaluation labels.
    All name variants → PERSON; all address variants → ADDRESS; others pass through.
    """
    label = label.upper()
    if label in NAME_LABELS:
        return CANONICAL_PERSON
    if label in ADDRESS_LABELS:
        return CANONICAL_ADDRESS
    return label


def map_model_label(raw_label: str) -> set:
    """
    Map a raw model output label (e.g. 'private_email') to the set of canonical
    labels it is considered equivalent to. Returns empty set if unknown.
    """
    return MODEL_TO_CANONICAL.get(raw_label.upper(), set())


# ─────────────────────────────────────────────────────────────────────────────
# 3. SPAN MERGING
# ─────────────────────────────────────────────────────────────────────────────

def merge_spans(spans: list[dict]) -> tuple[list[dict], int]:
    """
    Merge adjacent or overlapping spans that share the same canonical label set.

    Spans must have keys: value, start, end, label (already mapped canonical label).
    Returns (merged_spans, n_merges_performed).

    Example:
        [{'value':'1990A@aol','start':0,'end':9,'label':'EMAIL'},
         {'value':'.com',     'start':9,'end':13,'label':'EMAIL'}]
        → [{'value':'1990A@aol.com','start':0,'end':13,'label':'EMAIL'}]
    """
    if not spans:
        return [], 0

    # Sort by start position then by end position descending
    sorted_spans = sorted(spans, key=lambda s: (s["start"], -s["end"]))

    merged = [sorted_spans[0].copy()]
    n_merges = 0

    for current in sorted_spans[1:]:
        last = merged[-1]

        # Same label and adjacent or overlapping (allow gap of ≤1 char for e.g. space)
        same_label  = current["label"] == last["label"]
        adjacent    = current["start"] <= last["end"] + 1

        if same_label and adjacent:
            # Extend the last span to cover current
            last["end"]   = max(last["end"], current["end"])
            last["value"] = last["value"]  # raw value is approximate after merge
            n_merges += 1
        else:
            merged.append(current.copy())

    return merged, n_merges


# ─────────────────────────────────────────────────────────────────────────────
# 4. SPAN MATCHING
# ─────────────────────────────────────────────────────────────────────────────

def match_spans(
    predictions: list[dict],
    ground_truth: list[dict],
    mode: str = "in_scope"
) -> tuple[int, int, int, dict]:
    """
    Overlap-based span matching with one-to-one assignment.

    Args:
        predictions : list of {'value', 'start', 'end', 'label'} with canonical labels
        ground_truth: list of {'value', 'start', 'end', 'label'} with canonical labels
        mode        : 'in_scope' — only consider GT spans whose label is in
                                   IN_SCOPE_CANONICAL (fair evaluation)
                      'full'     — consider all GT spans (shows coverage penalty)

    Returns:
        tp, fp, fn, per_label_counts (dict of label → {tp, fp, fn})
    """
    if mode == "in_scope":
        active_gt = [gt for gt in ground_truth
                     if gt["label"] in IN_SCOPE_CANONICAL]
    else:
        active_gt = ground_truth

    tp, fp, fn = 0, 0, 0
    per_label: dict = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    matched_gt   = set()
    matched_pred = set()

    for pi, pred in enumerate(predictions):
        pred_label = pred["label"]          # single canonical label on the prediction
        matched = False

        for gi, gt in enumerate(active_gt):
            if gi in matched_gt:
                continue
            gt_label = gt["label"]     

            pred_targets = pred.get("canonical_targets", {pred_label})

            label_match  = gt_label in pred_targets
            span_overlap = pred["start"] < gt["end"] and pred["end"] > gt["start"]

            if label_match and span_overlap:
                tp += 1
                matched_gt.add(gi)
                matched_pred.add(pi)
                matched = True
                per_label[gt_label]["tp"] += 1
                break

        if not matched:
            fp += 1
            per_label[pred_label]["fp"] += 1

    for gi, gt in enumerate(active_gt):
        if gi not in matched_gt:
            fn += 1
            per_label[gt["label"]]["fn"] += 1

    return tp, fp, fn, dict(per_label)


# ─────────────────────────────────────────────────────────────────────────────
# 5. METRICS
# ─────────────────────────────────────────────────────────────────────────────

def compute_metrics(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    fnr       = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    fpr       = fp / (fp + tp) if (fp + tp) > 0 else 0.0
    return {
        "precision": round(precision, 4),
        "recall":    round(recall,    4),
        "f1":        round(f1,        4),
        "fnr":       round(fnr,       4),
        "fpr":       round(fpr,       4),
    }


def compute_coverage(ground_truth_all: list[list[dict]]) -> dict:
    """
    Coverage rate: fraction of unique GT labels (post-collapse) that fall within
    IN_SCOPE_CANONICAL, and fraction of GT span *instances* that are in-scope.
    """
    all_gt_labels = set()
    total_gt_spans = 0
    in_scope_spans = 0

    for gt_list in ground_truth_all:
        for gt in gt_list:
            collapsed = collapse_dataset_label(gt["label"])
            all_gt_labels.add(collapsed)
            total_gt_spans += 1
            if collapsed in IN_SCOPE_CANONICAL:
                in_scope_spans += 1

    in_scope_label_types = all_gt_labels & IN_SCOPE_CANONICAL
    unsupported_types    = all_gt_labels - IN_SCOPE_CANONICAL

    return {
        "total_gt_label_types":    len(all_gt_labels),
        "in_scope_label_types":    len(in_scope_label_types),
        "coverage_rate_labels":    round(len(in_scope_label_types) / len(all_gt_labels), 4)
                                   if all_gt_labels else 0.0,
        "total_gt_spans":          total_gt_spans,
        "in_scope_spans":          in_scope_spans,
        "coverage_rate_spans":     round(in_scope_spans / total_gt_spans, 4)
                                   if total_gt_spans else 0.0,
        "unsupported_label_types": sorted(unsupported_types),
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. MODEL LOADING & PREDICTION
# ─────────────────────────────────────────────────────────────────────────────

def load_model():
    print("Loading OpenAI Privacy Filter...")
    pii_pipeline = pipeline(
        "token-classification",
        model="openai/privacy-filter",
        aggregation_strategy="simple",
        trust_remote_code=True
    )
    print("Model loaded.\n")
    return pii_pipeline


def predict(pii_pipeline, text: str) -> list[dict]:
    """
    Run model inference and return spans with canonical labels + target sets.
    Spans are merged before being returned.
    """
    try:
        raw_results = pii_pipeline(text)
    except Exception as e:
        print(f"  [ERROR] prediction failed: {e}")
        return []

    # Map to canonical
    mapped = []
    for r in raw_results:
        raw_label      = r["entity_group"].upper()
        canonical_targets = map_model_label(raw_label)
        if not canonical_targets:
            canonical_targets = {raw_label}
        primary_label = sorted(canonical_targets)[0]
        mapped.append({
            "value":             r["word"],
            "start":             r["start"],
            "end":               r["end"],
            "label":             primary_label,
            "canonical_targets": canonical_targets,
            "raw_label":         raw_label,
        })

    merged, _ = merge_spans(mapped)
    for span in merged:
        if "canonical_targets" not in span:
            span["canonical_targets"] = map_model_label(span.get("raw_label", span["label"]))
            if not span["canonical_targets"]:
                span["canonical_targets"] = {span["label"]}
    return merged


def prepare_ground_truth(raw_gt: list[dict]) -> list[dict]:
    """Collapse dataset labels to canonical form."""
    result = []
    for item in raw_gt:
        collapsed = collapse_dataset_label(item["label"])
        result.append({
            "value": item.get("value", ""),
            "start": item["start"],
            "end":   item["end"],
            "label": collapsed,
        })
    return result


# ─────────────────────────────────────────────────────────────────────────────
# 7. DIAGNOSTICS
# ─────────────────────────────────────────────────────────────────────────────

class Diagnostics:
    def __init__(self):
        self.raw_model_label_counts:   defaultdict = defaultdict(int)
        self.canonical_pred_counts:    defaultdict = defaultdict(int)
        self.gt_label_counts_raw:      defaultdict = defaultdict(int)
        self.gt_label_counts_canon:    defaultdict = defaultdict(int)
        self.total_raw_pred_spans:     int = 0
        self.total_merged_pred_spans:  int = 0
        self.total_merges_performed:   int = 0
        self.span_correction_examples: list = []
        self.unsupported_gt_labels:    defaultdict = defaultdict(int)

    def record_raw_predictions(self, raw_preds: list[dict]):
        for p in raw_preds:
            self.raw_model_label_counts[p.get("raw_label", p["label"])] += 1
            self.total_raw_pred_spans += 1

    def record_merged_predictions(self, merged_preds: list[dict], n_merges: int):
        for p in merged_preds:
            self.canonical_pred_counts[p["label"]] += 1
        self.total_merged_pred_spans += len(merged_preds)
        self.total_merges_performed  += n_merges

    def record_gt(self, raw_gt: list[dict]):
        for gt in raw_gt:
            self.gt_label_counts_raw[gt["label"]] += 1
            self.gt_label_counts_canon[collapse_dataset_label(gt["label"])] += 1
            if collapse_dataset_label(gt["label"]) not in IN_SCOPE_CANONICAL:
                self.unsupported_gt_labels[collapse_dataset_label(gt["label"])] += 1

    def add_span_example(self, before: list[dict], after: list[dict]):
        if len(self.span_correction_examples) < 10 and len(before) > len(after):
            self.span_correction_examples.append({
                "before": [(s["value"], s["label"]) for s in before],
                "after":  [(s["value"], s["label"]) for s in after],
            })

    def print_report(self):
        print("\n" + "═"*60)
        print("DIAGNOSTICS")
        print("═"*60)

        print("\n── Raw model label distribution (before mapping) ──")
        for lbl, cnt in sorted(self.raw_model_label_counts.items(),
                                key=lambda x: -x[1]):
            print(f"  {lbl:<30} {cnt:>6}")

        print("\n── Canonical prediction label distribution (after mapping & merge) ──")
        for lbl, cnt in sorted(self.canonical_pred_counts.items(),
                                key=lambda x: -x[1]):
            print(f"  {lbl:<30} {cnt:>6}")

        print("\n── GT label distribution (raw dataset labels) ──")
        for lbl, cnt in sorted(self.gt_label_counts_raw.items(),
                                key=lambda x: -x[1]):
            print(f"  {lbl:<30} {cnt:>6}")

        print("\n── GT label distribution (after collapse) ──")
        for lbl, cnt in sorted(self.gt_label_counts_canon.items(),
                                key=lambda x: -x[1]):
            scope = "✓ in-scope" if lbl in IN_SCOPE_CANONICAL else "✗ out-of-scope"
            print(f"  {lbl:<30} {cnt:>6}  {scope}")

        print(f"\n── Span merging stats ──")
        print(f"  Raw predicted spans  : {self.total_raw_pred_spans}")
        print(f"  Merged predicted spans: {self.total_merged_pred_spans}")
        print(f"  Merges performed     : {self.total_merges_performed}")

        print(f"\n── Unsupported GT labels (counted as FN in FULL mode) ──")
        if self.unsupported_gt_labels:
            for lbl, cnt in sorted(self.unsupported_gt_labels.items(),
                                   key=lambda x: -x[1]):
                print(f"  {lbl:<30} {cnt:>6} spans")
        else:
            print("  None — all GT labels are in-scope.")

        if self.span_correction_examples:
            print(f"\n── Span merge examples (up to 10) ──")
            for i, ex in enumerate(self.span_correction_examples, 1):
                print(f"  [{i}] Before: {ex['before']}")
                print(f"      After : {ex['after']}")


# ─────────────────────────────────────────────────────────────────────────────
# 8. MAIN
# ─────────────────────────────────────────────────────────────────────────────

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

    pii_pipeline = load_model()

    # Aggregators
    scope_tp, scope_fp, scope_fn = 0, 0, 0
    full_tp,  full_fp,  full_fn  = 0, 0, 0

    scope_label_totals: dict = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    full_label_totals:  dict = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    lang_scope_totals:  dict = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    lang_full_totals:   dict = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    diag = Diagnostics()
    skipped = 0
    rows = []
    all_gt_raw = []  # for coverage computation

    for i, sample in enumerate(samples):
        if i % 100 == 0:
            print(f"  Processing {i}/{len(samples)}...")

        text         = sample["source_text"]
        raw_gt       = sample["privacy_mask"]
        language     = sample.get("language", "unknown")
        sample_id    = sample.get("id", str(i))

        if len(text) > 2000:
            skipped += 1
            continue

        # ── Ground truth: collapse labels ──
        diag.record_gt(raw_gt)
        all_gt_raw.append(raw_gt)
        gt_canonical = prepare_ground_truth(raw_gt)

        # ── Predictions: raw → mapped → merged ──
        # Get raw predictions before merging for diagnostics
        try:
            raw_results = pii_pipeline(text)
        except Exception as e:
            print(f"  [ERROR] {sample_id}: {e}")
            continue

        raw_mapped = []
        for r in raw_results:
            raw_label         = r["entity_group"].upper()
            canonical_targets = map_model_label(raw_label)
            if not canonical_targets:
                canonical_targets = {raw_label}
            primary_label = sorted(canonical_targets)[0]
            raw_mapped.append({
                "value":             r["word"],
                "start":             r["start"],
                "end":               r["end"],
                "label":             primary_label,
                "canonical_targets": canonical_targets,
                "raw_label":         raw_label,
            })

        diag.record_raw_predictions(raw_mapped)

        merged_preds, n_merges = merge_spans(raw_mapped)
        # Re-attach canonical_targets after merge (preserved from primary label)
        for span in merged_preds:
            if "canonical_targets" not in span:
                span["canonical_targets"] = map_model_label(span["label"])
                if not span["canonical_targets"]:
                    span["canonical_targets"] = {span["label"]}

        diag.record_merged_predictions(merged_preds, n_merges)
        diag.add_span_example(raw_mapped, merged_preds)

        # ── Evaluation: IN-SCOPE ──
        s_tp, s_fp, s_fn, s_per_label = match_spans(merged_preds, gt_canonical,
                                                      mode="in_scope")
        scope_tp += s_tp; scope_fp += s_fp; scope_fn += s_fn
        for lbl, c in s_per_label.items():
            for k in ("tp", "fp", "fn"):
                scope_label_totals[lbl][k] += c[k]
        for k in ("tp", "fp", "fn"):
            lang_scope_totals[language][k] += locals()[f"s_{k}"]

        # ── Evaluation: FULL ──
        f_tp, f_fp, f_fn, f_per_label = match_spans(merged_preds, gt_canonical,
                                                      mode="full")
        full_tp += f_tp; full_fp += f_fp; full_fn += f_fn
        for lbl, c in f_per_label.items():
            for k in ("tp", "fp", "fn"):
                full_label_totals[lbl][k] += c[k]
        for k in ("tp", "fp", "fn"):
            lang_full_totals[language][k] += locals()[f"f_{k}"]

        # Per-sample row (both modes)
        s_m = compute_metrics(s_tp, s_fp, s_fn)
        f_m = compute_metrics(f_tp, f_fp, f_fn)
        rows.append({
            "sample_id": sample_id,
            "language":  language,
            # in-scope
            "scope_tp": s_tp, "scope_fp": s_fp, "scope_fn": s_fn,
            "scope_precision": s_m["precision"],
            "scope_recall":    s_m["recall"],
            "scope_f1":        s_m["f1"],
            "scope_fnr":       s_m["fnr"],
            # full
            "full_tp": f_tp, "full_fp": f_fp, "full_fn": f_fn,
            "full_precision": f_m["precision"],
            "full_recall":    f_m["recall"],
            "full_f1":        f_m["f1"],
            "full_fnr":       f_m["fnr"],
            "model": "openai_privacy_filter"
        })

    print(f"\nSkipped samples (too long): {skipped}")

    # ── Coverage ──
    cov = compute_coverage(all_gt_raw)

    # ── Print results ──
    sep = "="*60

    print(f"\n{sep}")
    print("COVERAGE ANALYSIS")
    print(sep)
    print(f"  GT label types total      : {cov['total_gt_label_types']}")
    print(f"  In-scope label types      : {cov['in_scope_label_types']}")
    print(f"  Label coverage rate       : {cov['coverage_rate_labels']:.2%}")
    print(f"  GT spans total            : {cov['total_gt_spans']}")
    print(f"  In-scope GT spans         : {cov['in_scope_spans']}")
    print(f"  Span coverage rate        : {cov['coverage_rate_spans']:.2%}")
    print(f"  Unsupported label types   : {', '.join(cov['unsupported_label_types']) or 'None'}")

    def print_overall(label, tp, fp, fn):
        m = compute_metrics(tp, fp, fn)
        print(f"\n{sep}")
        print(f"OVERALL — {label}")
        print(sep)
        print(f"  TP: {tp}  FP: {fp}  FN: {fn}")
        print(f"  Precision : {m['precision']:.4f}")
        print(f"  Recall    : {m['recall']:.4f}")
        print(f"  F1        : {m['f1']:.4f}")
        print(f"  FNR       : {m['fnr']:.4f}")
        print(f"  FPR       : {m['fpr']:.4f}")

    print_overall("IN-SCOPE EVALUATION (fair — model-supported labels only)",
                  scope_tp, scope_fp, scope_fn)
    print_overall("FULL EVALUATION (all labels — includes coverage penalty)",
                  full_tp,  full_fp,  full_fn)

    def print_per_label(label_totals, title):
        print(f"\n{sep}")
        print(f"PER-LABEL — {title}")
        print(sep)
        header = f"{'Label':<25} {'TP':>6} {'FP':>6} {'FN':>6} {'Prec':>8} {'Rec':>8} {'F1':>8} {'FNR':>8}"
        print(header)
        for lbl, c in sorted(label_totals.items()):
            m = compute_metrics(c["tp"], c["fp"], c["fn"])
            scope_mark = "" if lbl in IN_SCOPE_CANONICAL else " *"
            print(f"{lbl+scope_mark:<25} {c['tp']:>6} {c['fp']:>6} {c['fn']:>6} "
                  f"{m['precision']:>8.4f} {m['recall']:>8.4f} {m['f1']:>8.4f} {m['fnr']:>8.4f}")
        if any(lbl not in IN_SCOPE_CANONICAL for lbl in label_totals):
            print("  * = out-of-scope label (model has no equivalent; FN is structural)")

    print_per_label(scope_label_totals, "IN-SCOPE")
    print_per_label(full_label_totals,  "FULL")

    def print_per_lang(lang_totals, title):
        print(f"\n{sep}")
        print(f"PER-LANGUAGE — {title}")
        print(sep)
        header = f"{'Language':<12} {'TP':>6} {'FP':>6} {'FN':>6} {'Prec':>8} {'Rec':>8} {'F1':>8} {'FNR':>8}"
        print(header)
        for lang, c in sorted(lang_totals.items()):
            m = compute_metrics(c["tp"], c["fp"], c["fn"])
            print(f"{lang:<12} {c['tp']:>6} {c['fp']:>6} {c['fn']:>6} "
                  f"{m['precision']:>8.4f} {m['recall']:>8.4f} {m['f1']:>8.4f} {m['fnr']:>8.4f}")

    print_per_lang(lang_scope_totals, "IN-SCOPE")
    print_per_lang(lang_full_totals,  "FULL")

    # ── Diagnostics ──
    diag.print_report()

    # ── Save CSV ──
    csv_path = "openai_results_fixed.csv"
    fieldnames = [
        "sample_id", "language",
        "scope_tp", "scope_fp", "scope_fn",
        "scope_precision", "scope_recall", "scope_f1", "scope_fnr",
        "full_tp",  "full_fp",  "full_fn",
        "full_precision",  "full_recall",  "full_f1",  "full_fnr",
        "model"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved per-sample results to {csv_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()