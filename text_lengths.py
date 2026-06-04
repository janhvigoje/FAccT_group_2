from datasets import load_dataset
import numpy as np

dataset = load_dataset("ai4privacy/pii-masking-300k")

lengths = [len(x["source_text"]) for x in dataset["train"]]

print("Mean:", np.mean(lengths))
print("Median:", np.median(lengths))
print("Min:", np.min(lengths))
print("Max:", np.max(lengths))

print("25th percentile:", np.percentile(lengths, 25))
print("75th percentile:", np.percentile(lengths, 75))