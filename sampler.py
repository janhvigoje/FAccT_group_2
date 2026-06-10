from datasets import load_dataset
import json
import random
 
random.seed(42)
 
print("Loading dataset...")
dataset = load_dataset("ai4privacy/pii-masking-300k")
val = dataset["validation"]
 
print(f"\nValidation set size: {len(val)}")
print(f"Features: {val.features}")
 
# Check a single sample to understand the format
print("\n--- Sample 0 ---")
sample = val[0]
for key, value in sample.items():
    print(f"{key}: {value}")
 
# Group by language
language_groups = {}
for i, example in enumerate(val):
    lang = example["language"]
    if lang not in language_groups:
        language_groups[lang] = []
    language_groups[lang].append(i)
 
print("\nLanguage distribution in validation set:")
for lang, indices in language_groups.items():
    print(f"  {lang}: {len(indices)} samples")
 
# Stratified sample: 500 per language
samples_per_language = 500
sampled_indices = []
 
for lang, indices in language_groups.items():
    n = min(samples_per_language, len(indices))
    sampled = random.sample(indices, n)
    sampled_indices.extend(sampled)
    print(f"Sampled {n} from {lang}")
 
print(f"\nTotal sampled: {len(sampled_indices)}")
 
# Save to sample.jsonl
output_path = "sample.jsonl"
with open(output_path, "w", encoding="utf-8") as f:
    for idx in sampled_indices:
        example = val[idx]
        f.write(json.dumps(example, ensure_ascii=False) + "\n")
 
print(f"\nSaved to {output_path}")
print("Done.")