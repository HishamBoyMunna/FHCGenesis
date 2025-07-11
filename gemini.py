import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyD2bK8Rov5AQeiFwnevXIux8BeHOtMFoe0")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how AI works in a few words",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
    ),
)
print(response.text)

