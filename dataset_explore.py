from datasets import load_dataset

dataset = load_dataset("ai4privacy/pii-masking-300k")

print(dataset)

print("\nTrain samples:", len(dataset["train"]))
print("Validation samples:", len(dataset["validation"]))

languages = set(dataset["train"]["language"])
print("\nLanguages:")
print(languages)