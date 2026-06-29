import os
import json
import pandas as pd

# ─────────────────────────────────────────────────────────────────────────────
# 1. Extract the six domains and split the data into short/long text groups (based on sample.jsonl)
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
# 2. Load the latest evaluation CSV
# ─────────────────────────────────────────────────────────────────────────────
print("Loading pre-computed CSV files...")
df_baseline = pd.read_csv("baseline_results.csv")
for col in ["language", "model"]:
    if col in df_baseline.columns: df_baseline = df_baseline.drop(columns=[col])

df_openai = pd.read_csv("openai_results_fixed.csv")
for col in ["language", "model"]:
    if col in df_openai.columns: df_openai = df_openai.drop(columns=[col])

df_b_merged = pd.merge(df_baseline, df_meta, on="sample_id")
df_o_merged = pd.merge(df_openai, df_meta, on="sample_id")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Compute evaluation metrics
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


# =============================================================================
# OPENAI PRIVACY FILTER BREAKDOWNS (i-v)
# =============================================================================
print("\n" + "=" * 80 + "\nOPENAI PRIVACY FILTER BREAKDOWNS (Dual-Mode)\n" + "=" * 80)

opf_pii_scope = {
    "EMAIL": [1040, 58, 0, 0.9472, 1.0000, 0.9729, 0.0000, 0.0528],
    "SOCIALNUMBER": [944, 0, 2, 1.0000, 0.9979, 0.9989, 0.0021, 0.0000],
    "IDCARD": [1051, 0, 52, 1.0000, 0.9529, 0.9759, 0.0471, 0.0000],
    "IP": [921, 118, 17, 0.8864, 0.9819, 0.9317, 0.0181, 0.1136],
    "TEL": [825, 87, 3, 0.9046, 0.9964, 0.9483, 0.0036, 0.0954],
    "PASS": [621, 53, 16, 0.9214, 0.9749, 0.9474, 0.0251, 0.0786],
    "DATE": [687, 1169, 17, 0.3702, 0.9759, 0.5367, 0.0241, 0.6298],
    "PERSON": [1763, 2193, 339, 0.4457, 0.8387, 0.5820, 0.1613, 0.5543],
    "ADDRESS": [1937, 1111, 1540, 0.6355, 0.5571, 0.5937, 0.4429, 0.3645],
    "ACCOUNTNUMBER": [0, 2127, 0, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000]
}
opf_pii_full = dict(opf_pii_scope)
# Add the 11 out-of-scope PII labels
opf_pii_full.update({
    "BOD *": [0, 0, 920, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "BUILDING *": [0, 0, 718, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "DRIVERLICENSE *": [0, 0, 988, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "GEOCOORD *": [0, 0, 79, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "LASTNAME3 *": [0, 0, 79, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "PASSPORT *": [0, 0, 1019, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "SECADDRESS *": [0, 0, 320, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "SEX *": [0, 0, 843, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "TIME *": [0, 0, 1539, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "TITLE *": [0, 0, 769, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
    "USERNAME *": [0, 0, 1078, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000]
})
print_tsv_block("(i) OpenAI Filter - PII Category Breakdown (In-Scope)",
                ["Category", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], opf_pii_scope)
print_tsv_block("(i) OpenAI Filter - PII Category Breakdown (Full)",
                ["Category", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], opf_pii_full)

# (ii) Language
o_lang_scope, o_lang_full = {}, {}
for lang, group in df_o_merged.groupby("language"):
    o_lang_scope[lang] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(), group["scope_fn"].sum())
    o_lang_full[lang] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(), group["full_fn"].sum())
print_tsv_block("(ii) OpenAI Filter - Language Breakdown (In-Scope)",
                ["Language", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_lang_scope)
print_tsv_block("(ii) OpenAI Filter - Language Breakdown (Full)",
                ["Language", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_lang_full)

# (iii) Domain
o_dom_scope, o_dom_full = {}, {}
for dom, group in df_o_merged.groupby("domain"):
    o_dom_scope[dom] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(), group["scope_fn"].sum())
    o_dom_full[dom] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(), group["full_fn"].sum())
print_tsv_block("(iii) OpenAI Filter - Domain Breakdown (In-Scope)",
                ["Domain", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_dom_scope)
print_tsv_block("(iii) OpenAI Filter - Domain Breakdown (Full)",
                ["Domain", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_dom_full)

# (iv) Length
o_len_scope, o_len_full = {}, {}
for lg, group in df_o_merged.groupby("length_group"):
    o_len_scope[lg] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(), group["scope_fn"].sum())
    o_len_full[lg] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(), group["full_fn"].sum())
print_tsv_block("(iv) OpenAI Filter - Text Length Breakdown (In-Scope)",
                ["Length Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_len_scope)
print_tsv_block("(iv) OpenAI Filter - Text Length Breakdown (Full)",
                ["Length Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_len_full)

# (v) Intersection
o_inter_scope, o_inter_full = {}, {}
for (dom, lg), group in df_o_merged.groupby(["domain", "length_group"]):
    o_inter_scope[f"{dom} ({lg})"] = compute_metrics(group["scope_tp"].sum(), group["scope_fp"].sum(),
                                                     group["scope_fn"].sum())
    o_inter_full[f"{dom} ({lg})"] = compute_metrics(group["full_tp"].sum(), group["full_fp"].sum(),
                                                    group["full_fn"].sum())
print_tsv_block("(v) OpenAI Filter - Intersectional (Domain x Length - In-Scope)",
                ["Intersectional Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_inter_scope)
print_tsv_block("(v) OpenAI Filter - Intersectional (Domain x Length - Full)",
                ["Intersectional Group", "TP", "FP", "FN", "Precision", "Recall", "F1", "FNR", "FPR"], o_inter_full)

print("\nSuccess! Copy the blocks above and paste directly into Google Sheets.")