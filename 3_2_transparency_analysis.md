# 3.2 Transparency Analysis

Privacy filters are often used before data is sent to another AI model or shared with other people and it is important that users understand what the model can and cannot do. A company should not only publish the overall performance of the model, but also explain its limitations. Otherwise, users may wrongly believe that all personal information has been removed.

## Label Taxonomy

One of the most important things that should be documented is which types of personal information the model can detect.

Our evaluation showed that the OpenAI Privacy Filter works very well for common identifiers such as email addresses, phone numbers and passwords. However, many other PII categories from the AI4Privacy dataset are not supported.

Some examples are:

- Passport numbers
- Driver's licence numbers
- Usernames
- IP addresses
- Birth dates
- Name labels

If useers do not know about these limitations, theyy may think that all personal information has been removed even though some identifiers are still visible.

## Training and Evaluation Data

The provider should also explain what kind of data was used to train and evaluate the model.

For example, it would be useful to know:

- Which languages were included
- Which document types were used
- Which PII categories were part of the training data

Without this information, it is difficult for organizations to know if the model is suitable for their own documents.

## Known Failure Modes

The documentation should also include common mistakes that the model makes.

### Under redaction

Under redaction happens when the model misses personal information that should have been masked.

In our evaluation, this happened for identifiers such as passport numbers, birth dates and other unsupported categories. This is the most serious type of error because sensitive information stays visible.

### Over redaction

Over redaction happens when the model masks information that is not actually personal.

For example, certificate IDs were sometimes classified as account or social security numbers. Zhis does not create a privacy risk, but it removes useful information from the document.

## Subgroup Performance

Instead of only reporting  one overall F1-score, the provider should also publish results for different groups.

Our evaluation showed that the model performed similarly across different languages, but there were large differences between PII categories. Some categories had very high recall, while others were never detected.

Showing these results would help users to understand where the model performs well and where it has weaknesses.

## Threshold Choices

The provider should also explain how the model decides whether something should be masked.

Changing the threshold can change the balance between missing identifiers and masking too much information. Giving users information about this threshold or allowing them to adjust it would help them choose the best setting for their own application.

## Intended and Non-intended Uses

Based on our evaluation, the OpenAI Privacy Filter is useful as a first step for anaonymizing common personal information such as email addresses and phone numbers.

However, it should not be used as the only privacy protection method. For sensitive documents such as medical or legal records, the results should still be checked manually or combined with other privacy tools.

## Conclusion

Transparency is very important for privacy filters, even more important than a single overall performance score. An overall score can be misleading because it may suggest that the filter performs better than it actually does. Users also need information about the model's known limitations, the PII categories it supports and the situations where it performs well or poorly. This allows organizations to better understand the risks of using the model and decide whether it is suitable for their specific use case.