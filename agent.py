
import os
from dotenv import load_dotenv
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

# -----------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# -----------------------------------

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://api.groq.com/openai/v1"
)
MODEL_NAME = os.getenv("MODEL_NAME", "openai/gpt-oss-120b")


# -----------------------------------
# 2. VALIDATE CONFIGURATION
# -----------------------------------

if not API_KEY:
    raise ValueError(
        "OPENAI_API_KEY is missing. Check your .env file "
        "or Streamlit Cloud Secrets."
    )

if not MODEL_NAME:
    raise ValueError("MODEL_NAME is missing.")


# -----------------------------------
# 3. CREATE GROQ CLIENT
# -----------------------------------

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=60.0,
    max_retries=2
)


# -----------------------------------
# 4. ASK AI AGENT
# -----------------------------------

def ask_agent(messages):

    if not isinstance(messages, list) or not messages:
        raise ValueError("Messages must be a non-empty list.")

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError("The AI returned an empty response.")

        return answer.strip()

    except AuthenticationError as error:
        print("Groq authentication error:", error)
        raise RuntimeError(
            "Groq API authentication failed. Check your API key."
        ) from error

    except RateLimitError as error:
        print("Groq rate limit error:", error)
        raise RuntimeError(
            "Groq API rate limit reached. Please try again later."
        ) from error

    except APIError as error:
        print("Groq API error:", error)
        raise RuntimeError(
            "Groq AI service returned an API error."
        ) from error

    except Exception as error:
        print("AI connection error:", error)
        raise RuntimeError(
            "Unable to connect to Groq. Check your settings "
            "and internet connection."
        ) from error
