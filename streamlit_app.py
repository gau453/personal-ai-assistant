
import os
import streamlit as st
from dotenv import load_dotenv

# -----------------------------------
# 1. LOAD API SETTINGS
# -----------------------------------

load_dotenv()

def get_setting(key):
    """Read from Streamlit Cloud Secrets first, then local .env."""
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(key)


api_key = get_setting("OPENAI_API_KEY")
base_url = get_setting("OPENAI_BASE_URL")
model_name = get_setting("MODEL_NAME")

if not api_key or not model_name:
    st.error(
        "API settings are missing. Check your .env file "
        "or Streamlit Cloud Secrets."
    )
    st.stop()

# Set environment variables before importing agent.py
os.environ["OPENAI_API_KEY"] = api_key
os.environ["MODEL_NAME"] = model_name

if base_url:
    os.environ["OPENAI_BASE_URL"] = base_url
else:
    os.environ.pop("OPENAI_BASE_URL", None)


# -----------------------------------
# 2. IMPORT PROJECT FUNCTIONS
# -----------------------------------

from agent import ask_agent
from memory import (
    create_memory_table,
    save_memory,
    get_memory,
    get_all_memories,
    delete_memory
)
from tools import (
    create_task_table,
    add_task,
    get_tasks,
    complete_task
)


# -----------------------------------
# 3. PAGE CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Personal AI Assistant")
st.caption("Your AI assistant for conversations, memories and tasks.")

# Create database tables
create_memory_table()
create_task_table()


# -----------------------------------
# 4. SESSION STATE
# -----------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -----------------------------------
# 5. MEMORY CONTEXT
# -----------------------------------

def build_memory_context():
    memories = get_all_memories()

    if not memories:
        return "No saved memories."

    result = []

    for item in memories:
        result.append(f"{item[1]}: {item[2]}")

    return "\n".join(result)


# -----------------------------------
# 6. COMMAND HANDLER
# -----------------------------------

def handle_command(user_input):
    text = user_input.strip()
    lower = text.lower()

    # Help
    if lower == "help":
        return """
Available commands:

MEMORY:
remember learning: your information
remember my personal info: your information
retrieve learning: keyword
show memories
forget: memory_key

TASKS:
add task: task name
show tasks
complete task: task ID

Type anything else to chat with the AI.
"""

    # Show memories
    if lower == "show memories":
        memories = get_all_memories()

        if not memories:
            return "You have no saved memories."

        return "\n".join(
            [f"{item[1]}: {item[2]}" for item in memories]
        )

    # Remember learning
    if lower.startswith("remember learning:"):
        value = text.split(":", 1)[1].strip()

        if not value:
            return "Please provide something to remember."

        save_memory("learning", value)
        return "Learning saved successfully!"

    # Remember personal information
    if lower.startswith("remember my personal info:"):
        value = text.split(":", 1)[1].strip()

        if not value:
            return "Please provide information to remember."

        save_memory("personal_info", value)
        return "Personal information saved!"

    # Retrieve learning
    if lower.startswith("retrieve learning:"):
        key = text.split(":", 1)[1].strip()
        memory = get_memory(key)

        if memory:
            return f"Saved memory: {memory[2]}"

        return "No matching memory found."

    # Forget memory
    if lower.startswith("forget:"):
        key = text.split(":", 1)[1].strip()

        if not key:
            return "Please provide a memory key."

        delete_memory(key)
        return "Memory deletion requested."

    # Add task
    if lower.startswith("add task:"):
        task = text.split(":", 1)[1].strip()

        if not task:
            return "Please provide a task."

        add_task(task)
        return "Task added successfully!"

    # Show tasks
    if lower == "show tasks":
        tasks = get_tasks()

        if not tasks:
            return "You have no tasks."

        return "\n".join(
            [
                f"ID: {task[0]} | {task[1]} | "
                f"{'Completed' if task[2] else 'Pending'}"
                for task in tasks
            ]
        )

    # Complete task
    if lower.startswith("complete task:"):
        task_id = text.split(":", 1)[1].strip()

        if not task_id.isdigit():
            return "Please enter a valid task ID."

        complete_task(int(task_id))
        return "Task completion updated."

    return None


# -----------------------------------
# 7. SIDEBAR
# -----------------------------------

with st.sidebar:
    st.header("📌 Assistant Features")

    st.markdown("""
    - 💬 AI Chat
    - 🧠 Memory Storage
    - 📝 Task Management
    - 🔍 Memory Retrieval
    """)

    st.divider()

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()

    st.caption("Type `help` in the chat to see commands.")


# -----------------------------------
# 8. DISPLAY CHAT HISTORY
# -----------------------------------

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------------
# 9. CHAT INPUT AND AI RESPONSE
# -----------------------------------

user_input = st.chat_input("Message your AI assistant...")

if user_input:

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        try:
            command_response = handle_command(user_input)

            if command_response is not None:
                response = command_response

            else:
                memory_context = build_memory_context()

                system_message = {
                    "role": "system",
                    "content": (
                        "You are a helpful personal AI assistant. "
                        "Use the following saved memory when relevant:\n"
                        + memory_context
                    )
                }

                # Keep recent conversation context
                recent_messages = st.session_state.messages[-10:]

                messages = [
                    system_message
                ] + recent_messages + [
                    {"role": "user", "content": user_input}
                ]

                response = ask_agent(messages)

                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input
                })

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

            st.markdown(response)

        except Exception as error:
            response = (
                "Something went wrong while processing your request. "
                "Please check your configuration and try again."
            )
            st.error(response)
            print("Application error:", type(error).__name__)
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })
