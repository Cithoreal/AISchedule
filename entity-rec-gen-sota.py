

# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text-generation", model="openchat/openchat_3.5")

# # Example usage
print(pipe("Hello, how are you?"))



