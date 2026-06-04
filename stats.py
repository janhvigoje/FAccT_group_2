from datasets import load_dataset
from collections import Counter

dataset = load_dataset("ai4privacy/pii-masking-300k")

counter = Counter()

for sample in dataset["train"]:
    for entity in sample["privacy_mask"]:
        counter[entity["label"]] += 1

print("\nPII categories:")
for label, count in counter.most_common():
    print(f"{label}: {count}")