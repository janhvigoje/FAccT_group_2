import json
from transformers import pipeline

print("Loading model...")

pii_pipeline = pipeline(
    "token-classification",
    model="openai/privacy-filter",
    aggregation_strategy="simple",
    trust_remote_code=True
)

print("Model loaded.")

# -----------------------------
# CONFIG
# -----------------------------
MAX_SAMPLES = 100

# -----------------------------
# LOAD SAMPLES (LIMITED)
# -----------------------------
with open("sample.jsonl", "r", encoding="utf-8") as f:
    samples = [
        json.loads(line)
        for i, line in enumerate(f)
        if i < MAX_SAMPLES
    ]

# -----------------------------
# LABEL MAPPING
# -----------------------------
NAME_LABELS = {
    "GIVENNAME1", "GIVENNAME2",
    "LASTNAME1", "LASTNAME2", "MIDDLENAME"
}

ADDRESS_LABELS = {
    "STREET", "CITY", "STATE",
    "POSTCODE", "COUNTRY", "COUNTY",
    "ORDINALDIRECTION"
}

MODEL_MAP = {
    "PRIVATE_EMAIL": "EMAIL",
    "PRIVATE_PHONE": "TEL",
    "PRIVATE_URL": "URL",
    "PRIVATE_DATE": "DATE",
    "PRIVATE_PERSON": "PERSON",
    "PRIVATE_ADDRESS": "ADDRESS",
    "ACCOUNT_NUMBER": "SOCIALNUMBER",
    "SECRET": "PASS"
}

def collapse(label):
    label = label.upper()

    if label in NAME_LABELS:
        return "PERSON"

    if label in ADDRESS_LABELS:
        return "ADDRESS"

    return label

# -----------------------------
# EVALUATION STORAGE
# -----------------------------
false_negatives = []
false_positives = []

# -----------------------------
# MAIN LOOP
# -----------------------------
for sample in samples:
    text = sample["source_text"]

    gt = []
    for item in sample["privacy_mask"]:
        gt.append({
            "label": collapse(item["label"]),
            "start": item["start"],
            "end": item["end"],
            "value": item["value"]
        })

    preds = []

    try:
        result = pii_pipeline(text)
    except Exception:
        continue

    for r in result:
        label = MODEL_MAP.get(
            r["entity_group"].upper(),
            r["entity_group"].upper()
        )

        preds.append({
            "label": label,
            "start": r["start"],
            "end": r["end"],
            "value": r["word"]
        })

    # -----------------------------
    # FALSE NEGATIVES
    # -----------------------------
    for g in gt:
        matched = False

        for p in preds:
            overlap = (
                p["start"] < g["end"] and
                p["end"] > g["start"]
            )

            if overlap and p["label"] == g["label"]:
                matched = True
                break

        if not matched:
            false_negatives.append({
                "text": text,
                "ground_truth": g
            })

    # -----------------------------
    # FALSE POSITIVES
    # -----------------------------
    for p in preds:
        matched = False

        for g in gt:
            overlap = (
                p["start"] < g["end"] and
                p["end"] > g["start"]
            )

            if overlap and p["label"] == g["label"]:
                matched = True
                break

        if not matched:
            false_positives.append({
                "text": text,
                "prediction": p
            })

# -----------------------------
# SAVE RESULTS
# -----------------------------
with open("false_negatives.json", "w", encoding="utf-8") as f:
    json.dump(false_negatives, f, indent=2, ensure_ascii=False)

with open("false_positives.json", "w", encoding="utf-8") as f:
    json.dump(false_positives, f, indent=2, ensure_ascii=False)

print()
print("False negatives:", len(false_negatives))
print("False positives:", len(false_positives))
print()
print("Saved:")
print("false_negatives.json")
print("false_positives.json")