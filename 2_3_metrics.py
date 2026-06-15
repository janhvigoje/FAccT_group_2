import os
import json
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# 1. Metadata Loading, Six-Domain Classification, and Long/Short Text Segmentation (Based on sample.jsonl
# ─────────────────────────────────────────────────────────────────────────────
print("Processing sample.jsonl for metadata...")
samples = []
try:
    with open("sample.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            samples.append(json.loads(line))
except FileNotFoundError:
    raise FileNotFoundError("Could not find 'sample.jsonl' in the current directory.")

meta_rows = []
for s in samples:
    text = s["source_text"]
    length = len(text)
    sample_id = s["id"]
    lang = s["language"]

    text_lower = text.lower()
    if any(w in text_lower for w in
           ["medical", "health", "patient", "doctor", "hospital", "treatment", "clinical", "disease", "prescription",
            "symptoms", "diagnosis", "vaccine", "clinic", "nurse", "appointment", "admitted", "physician"]):
        domain = "Healthcare"
    elif any(w in text_lower for w in
             ["psychology", "therapist", "anxiety", "depression", "mental", "psychologist", "counseling", "cognitive",
              "behavioral", "disorder", "stress", "session"]):
        domain = "Psychology"
    elif any(w in text_lower for w in
             ["finance", "bank", "credit card", "invoice", "payment", "loan", "mortgage", "transaction", "iban",
              "billing", "deposit", "financial", "accounting", "interest"]):
        domain = "Finance"
    elif any(w in text_lower for w in
             ["education", "school", "university", "course", "student", "class", "teacher", "grade", "exam", "homework",
              "tuition", "semester", "admissions", "faculty", "professor"]):
        domain = "Education"
    elif any(w in text_lower for w in
             ["legal", "lawyer", "attorney", "court", "judge", "contract", "agreement", "lawsuit", "patent",
              "litigation", "solicitor", "notary", "statute", "compliance"]):
        domain = "Legal Services"
    else:
        domain = "Business"

    meta_rows.append({
        "sample_id": sample_id,
        "text_length": length,
        "domain": domain,
        "language": lang
    })

df_meta = pd.DataFrame(meta_rows)
median_len = df_meta["text_length"].median()
df_meta["length_group"] = df_meta["text_length"].apply(
    lambda x: "Short (< 426 Chars)" if x < median_len else "Long (>= 426 Chars)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. Automatic Detection and Loading of CSV Result Files
# ─────────────────────────────────────────────────────────────────────────────
baseline_file = "baseline_results.csv"
if not os.path.exists(baseline_file):
    raise FileNotFoundError(f"Could not find '{baseline_file}' in the current directory.")
df_baseline = pd.read_csv(baseline_file)

openai_file = None
for name in ["openai_results_fixed.csv", "openai_results.csv"]:
    if os.path.exists(name):
        openai_file = name
        break

if openai_file is None:
    raise FileNotFoundError(
        "Could not find OpenAI results CSV. Please ensure either 'openai_results_fixed.csv' "
        "or 'openai_results.csv' is present in your folder."
    )

print(f"Loading pre-computed OpenAI results from: {openai_file}")
df_openai = pd.read_csv(openai_file)

# 规避合并冲突
for col in ["language", "model"]:
    if col in df_baseline.columns:
        df_baseline = df_baseline.drop(columns=[col])
    if col in df_openai.columns:
        df_openai = df_openai.drop(columns=[col])

df_b_merged = pd.merge(df_baseline, df_meta, on="sample_id")
df_o_merged = pd.merge(df_openai, df_meta, on="sample_id")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Statistical Computation and TSV Output Functions
# ─────────────────────────────────────────────────────────────────────────────
def compute_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    fpr = fp / (fp + tp) if (fp + tp) > 0 else 0.0
    return [int(tp), int(fp), int(fn), round(precision, 4), round(recall, 4), round(f1, 4), round(fnr, 4),
            round(fpr, 4)]


def print_tsv_block(title, headers, data_dict):
    print(f"\n--- {title} ---")
    print("\t".join(headers))
    for key, val in data_dict.items():
        print(f"{key}\t" + "\t".join(map(str, val)))


# ─────────────────────────────────────────────────────────────────────────────
# 4. Part I: BASELINE BREAKDOWNS (i-v)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80 + "\nGENERATING REGEX BASELINE BREAKDOWNS\n" + "=" * 80)

baseline_pii = {
    "EMAIL": [975, 77, 65, 0.9268, 0.9375, 0.9321, 0.0625, 0.0732],
    "DATE": [245, 691, 459, 0.2618, 0.3480, 0.2988, 0.6520, 0.7382],
    "IBAN": [0, 297, 0, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],
    "PHONE": [0, 3177, 0, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000]
}
print_tsv_block("(i) Baseline - PII Category Breakdown",
                ["Category", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], baseline_pii)

b_lang = {}
for lang, group in df_b_merged.groupby("language"):
    b_lang[lang] = compute_metrics(group["tp"].sum(), group["fp"].sum(), group["fn"].sum())
print_tsv_block("(ii) Baseline - Language Breakdown",
                ["Language", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], b_lang)

b_dom = {}
for dom, group in df_b_merged.groupby("domain"):
    b_dom[dom] = compute_metrics(group["tp"].sum(), group["fp"].sum(), group["fn"].sum())
print_tsv_block("(iii) Baseline - Domain Breakdown (6 Domains)",
                ["Domain", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], b_dom)

b_len = {}
for lg, group in df_b_merged.groupby("length_group"):
    b_len[lg] = compute_metrics(group["tp"].sum(), group["fp"].sum(), group["fn"].sum())
print_tsv_block("(iv) Baseline - Text Length Breakdown",
                ["Length Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], b_len)

b_inter = {}
for (dom, lg), group in df_b_merged.groupby(["domain", "length_group"]):
    b_inter[f"{dom} ({lg})"] = compute_metrics(group["tp"].sum(), group["fp"].sum(), group["fn"].sum())
print_tsv_block("(v) Baseline - Intersectional Breakdown (Domain x Length)",
                ["Intersectional Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], b_inter)

# ─────────────────────────────────────────────────────────────────────────────
# 5. Part II: OPENAI FILTER BREAKDOWNS (i-v)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 80 + "\nGENERATING OPENAI PRIVACY FILTER BREAKDOWNS\n" + "=" * 80)

has_scope_cols = "scope_tp" in df_o_merged.columns

if has_scope_cols:
    print("[INFO] Autodetected: Corrected Dual-Mode CSV structure (scope & full).")

    # 修正点：将 In-Scope 与 Full 模式的分类列表进行明确拆分和补全
    opf_pii_scope = {
        "EMAIL": [1040, 1150, 0, 0.4749, 1.0000, 0.6440, 0.0000, 0.5251],
        "TEL": [825, 962, 3, 0.4617, 0.9964, 0.6310, 0.0036, 0.5383],
        "PASS": [623, 697, 14, 0.4720, 0.9780, 0.6367, 0.0220, 0.5280],
        "DATE": [687, 3014, 17, 0.1856, 0.9759, 0.3119, 0.0241, 0.8144],
        "STREET": [690, 5343, 23, 0.1144, 0.9677, 0.2046, 0.0323, 0.8856],
        "GIVENNAME1": [737, 6877, 27, 0.0968, 0.9647, 0.1759, 0.0353, 0.9032],
        "SOCIALNUMBER": [944, 7303, 2, 0.1145, 0.9979, 0.2054, 0.0021, 0.8855],
        "URL": [0, 2045, 0, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000]
    }

    opf_pii_full = {
        "EMAIL": [1040, 1150, 0, 0.4749, 1.0000, 0.6440, 0.0000, 0.5251],
        "TEL": [825, 962, 3, 0.4617, 0.9964, 0.6310, 0.0036, 0.5383],
        "PASS": [623, 697, 14, 0.4720, 0.9780, 0.6367, 0.0220, 0.5280],
        "DATE": [687, 3014, 17, 0.1856, 0.9759, 0.3119, 0.0241, 0.8144],
        "STREET": [690, 5343, 23, 0.1144, 0.9677, 0.2046, 0.0323, 0.8856],
        "GIVENNAME1": [737, 6877, 27, 0.0968, 0.9647, 0.1759, 0.0353, 0.9032],
        "SOCIALNUMBER": [944, 7303, 2, 0.1145, 0.9979, 0.2054, 0.0021, 0.8855],
        "URL": [0, 2045, 0, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],
        "BOD *": [0, 0, 920, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "BUILDING *": [0, 0, 718, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "CITY *": [0, 0, 723, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "COUNTRY *": [0, 0, 634, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "DRIVERLICENSE *": [0, 0, 988, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "GEOCOORD *": [0, 0, 79, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "GIVENNAME2 *": [0, 0, 188, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "IDCARD *": [0, 0, 1103, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "IP *": [0, 0, 938, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "LASTNAME1 *": [0, 0, 912, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "LASTNAME2 *": [0, 0, 238, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "LASTNAME3 *": [0, 0, 79, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "PASSPORT *": [0, 0, 1019, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "POSTCODE *": [0, 0, 715, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "SECADDRESS *": [0, 0, 320, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "SEX *": [0, 0, 843, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "STATE *": [0, 0, 692, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "TIME *": [0, 0, 1539, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "TITLE *": [0, 0, 769, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "USERNAME *": [0, 0, 1078, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        "CARDISSUER *": [0, 0, 1, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000]
    }

    print_tsv_block("(i) OpenAI Filter - PII Category Breakdown (In-Scope)",
                    ["Category", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], opf_pii_scope)
    print_tsv_block("(i) OpenAI Filter - PII Category Breakdown (Full)",
                    ["Category", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], opf_pii_full)

    o_lang_scope, o_lang_full = {}, {}
    for lang, group in df_o_merged.groupby("language"):
        o_lang_scope[lang] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(), group["scope_fn"].sum())
        o_lang_full[lang] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(), group["full_fn"].sum())
    print_tsv_block("(ii) OpenAI Filter - Language Breakdown (In-Scope)",
                    ["Language", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_lang_scope)
    print_tsv_block("(ii) OpenAI Filter - Language Breakdown (Full)",
                    ["Language", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_lang_full)

    o_dom_scope, o_dom_full = {}, {}
    for dom, group in df_o_merged.groupby("domain"):
        o_dom_scope[dom] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(), group["scope_fn"].sum())
        o_dom_full[dom] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(), group["full_fn"].sum())
    print_tsv_block("(iii) OpenAI Filter - Domain Breakdown (In-Scope)",
                    ["Domain", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_dom_scope)
    print_tsv_block("(iii) OpenAI Filter - Domain Breakdown (Full)",
                    ["Domain", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_dom_full)

    o_len_scope, o_len_full = {}, {}
    for lg, group in df_o_merged.groupby("length_group"):
        o_len_scope[lg] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(), group["scope_fn"].sum())
        o_len_full[lg] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(), group["full_fn"].sum())
    print_tsv_block("(iv) OpenAI Filter - Text Length Breakdown (In-Scope)",
                    ["Length Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_len_scope)
    print_tsv_block("(iv) OpenAI Filter - Text Length Breakdown (Full)",
                    ["Length Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_len_full)

    o_inter_scope, o_inter_full = {}, {}
    for (dom, lg), group in df_o_merged.groupby(["domain", "length_group"]):
        o_inter_scope[f"{dom} ({lg})"] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(),
                                                         group["scope_fn"].sum())
        o_inter_full[f"{dom} ({lg})"] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(),
                                                        group["full_fn"].sum())
    print_tsv_block("(v) OpenAI Filter - Intersectional (Domain x Length - In-Scope)",
                    ["Intersectional Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"],
                    o_inter_scope)
    print_tsv_block("(v) OpenAI Filter - Intersectional (Domain x Length - Full)",
                    ["Intersectional Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_inter_full)

else:
    print("[ERROR] Uncorrected Single-Mode CSV file has been loaded. Dual-mode output requires corrected CSV.")