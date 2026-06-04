from datasets import load_dataset

dataset = load_dataset("ai4privacy/pii-masking-300k")

print(dataset)
print(dataset["train"][0])