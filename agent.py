
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")

# Check configuration
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is missing from your .env file.")

if not MODEL_NAME:
    raise ValueError("MODEL_NAME is missing from your .env file.")

# Create AI client
client = OpenAI(
    base_url=BASE_URL or None,
    api_key=API_KEY
)


# =====================================
# ASK THE AI
# =====================================

def ask_agent(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as error:
        print("AI connection error:", error)
        return "Sorry, I couldn't connect to the AI service. Please check your API settings and internet connection."
