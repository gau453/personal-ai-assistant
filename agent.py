
import os
from dotenv import load_dotenv

from openai import (
    OpenAI,
    APIError,
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError
)


# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://api.groq.com/openai/v1"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-oss-120b"
)


# ==========================================
# 2. VALIDATE CONFIGURATION
# ==========================================

if not API_KEY:
    raise ValueError(
        "Groq API key is missing. "
        "Check Streamlit Secrets or your .env file."
    )

if not BASE_URL:
    raise ValueError("Groq API base URL is missing.")

if not MODEL_NAME:
    raise ValueError("Groq model name is missing.")


# ==========================================
# 3. CREATE GROQ CLIENT
# ==========================================

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
    timeout=60.0,
    max_retries=2
)


# ==========================================
# 4. VALIDATE CONVERSATION MESSAGES
# ==========================================

def validate_messages(messages):

    if not isinstance(messages, list) or not messages:
        raise ValueError(
            "Messages must be a non-empty list."
        )

    allowed_roles = {
        "system",
        "user",
        "assistant"
    }

    for message in messages:

        if not isinstance(message, dict):
            raise ValueError(
                "Every message must be a dictionary."
            )

        if message.get("role") not in allowed_roles:
            raise ValueError(
                "Invalid conversation message role."
            )

        if not isinstance(message.get("content"), str):
            raise ValueError(
                "Message content must be text."
            )

        if not message["content"].strip():
            raise ValueError(
                "Message content cannot be empty."
            )


# ==========================================
# 5. ASK AI AGENT
# ==========================================

def ask_agent(messages):

    validate_messages(messages)

    try:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )

        # Check response structure.

        if not response.choices:
            raise RuntimeError(
                "Groq returned no response choices."
            )

        answer = response.choices[0].message.content

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError(
                "AI Agent returned an empty response."
            )

        return answer.strip()


    # ======================================
    # 6. ERROR HANDLING
    # ======================================

    except AuthenticationError as error:

        print("Groq authentication failed.")

        raise RuntimeError(
            "Invalid Groq API key. Check your configuration."
        ) from error


    except RateLimitError as error:

        print("Groq rate limit reached.")

        raise RuntimeError(
            "Groq API rate limit reached. Please try again later."
        ) from error


    except APITimeoutError as error:

        print("Groq request timed out.")

        raise RuntimeError(
            "Groq took too long to respond. Please try again."
        ) from error


    except APIConnectionError as error:

        print("Unable to connect to Groq.")

        raise RuntimeError(
            "Could not connect to Groq. Check your connection."
        ) from error


    except APIError as error:

        print(
            "Groq API returned an error:",
            type(error).__name__
        )

        raise RuntimeError(
            "Groq AI service returned an API error. "
            "Check the model and API configuration."
        ) from error


    except RuntimeError:
        raise


    except Exception as error:

        print(
            "Unexpected AI error:",
            type(error).__name__
        )

        raise RuntimeError(
            "An unexpected error occurred while contacting Groq."
        ) from error
