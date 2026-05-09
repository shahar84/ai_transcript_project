from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are a helpful assistant.",
    input="How do I check if a Python object is an instance of a class?",
)

print(response.output_text)
