
import os
import streamlit as st
from dotenv import load_dotenv

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="centered"
)

# ==========================================
# 2. LOAD API SETTINGS
# ==========================================

load_dotenv()


def get_setting(key, default=None):
    """Read settings from Streamlit Secrets or local .env."""

    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(key, default)


api_key = get_setting("OPENAI_API_KEY")

base_url = get_setting(
    "OPENAI_BASE_URL",
    "https://api.groq.com/openai/v1"
)

model_name = get_setting(
    "MODEL_NAME",
    "openai/gpt-oss-120b"
)

if not api_key or not model_name:
    st.error(
        "API settings are missing. "
        "Please configure your Groq API key and model name "
        "in Streamlit Secrets or your local .env file."
    )
    st.stop()


# Set environment variables before importing agent.py

os.environ["OPENAI_API_KEY"] = api_key
os.environ["OPENAI_BASE_URL"] = base_url
os.environ["MODEL_NAME"] = model_name


# ==========================================
# 3. IMPORT PROJECT FUNCTIONS
# ==========================================

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


# ==========================================
# 4. APPLICATION HEADER
# ==========================================

st.title("🤖 AI Agent")

st.caption(
    "Your personal AI assistant for conversations, "
    "learning, memories and tasks."
)


# ==========================================
# 5. DATABASE INITIALIZATION
# ==========================================

create_memory_table()
create_task_table()


# ==========================================
# 6. SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==========================================
# 7. BUILD MEMORY CONTEXT
# ==========================================

def build_memory_context():

    memories = get_all_memories()

    if not memories:
        return "No saved memories."

    result = []

    for item in memories:
        result.append(
            f"{item[1]}: {item[2]}"
        )

    return "\n".join(result)


# ==========================================
# 8. COMMAND HANDLER
# ==========================================

def handle_command(user_input):

    text = user_input.strip()
    lower = text.lower()

    # HELP COMMAND

    if lower == "help":

        return """
### AI Agent Commands

**MEMORY MANAGEMENT**

- `remember learning: your information`
- `remember my personal info: your information`
- `retrieve learning: learning`
- `show memories`
- `forget: learning`

**TASK MANAGEMENT**

- `add task: task name`
- `show tasks`
- `complete task: task ID`

You can also chat naturally with AI Agent.
"""

    # SHOW MEMORIES

    if lower == "show memories":

        memories = get_all_memories()

        if not memories:
            return "You have no saved memories."

        return "\n".join(
            f"{item[1]}: {item[2]}"
            for item in memories
        )

    # SAVE LEARNING

    if lower.startswith("remember learning:"):

        value = text.split(":", 1)[1].strip()

        if not value:
            return "Please provide something to remember."

        return save_memory("learning", value)

    # SAVE PERSONAL INFORMATION

    if lower.startswith("remember my personal info:"):

        value = text.split(":", 1)[1].strip()

        if not value:
            return "Please provide personal information."

        return save_memory("personal_info", value)

    # RETRIEVE LEARNING

    if lower.startswith("retrieve learning:"):

        key = text.split(":", 1)[1].strip()

        memory = get_memory(key)

        if memory:
            return f"Saved memory: {memory[2]}"

        return "No matching memory found."

    # DELETE MEMORY

    if lower.startswith("forget:"):

        key = text.split(":", 1)[1].strip()

        if not key:
            return "Please provide a memory key."

        return delete_memory(key)

    # ADD TASK

    if lower.startswith("add task:"):

        task = text.split(":", 1)[1].strip()

        if not task:
            return "Please provide a task."

        return add_task(task)

    # SHOW TASKS

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

    # COMPLETE TASK

    if lower.startswith("complete task:"):

        task_id = text.split(":", 1)[1].strip()

        if not task_id.isdigit():
            return "Please enter a valid task ID."

        return complete_task(int(task_id))

    return None


# ==========================================
# 9. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🤖 AI Agent")

    st.caption("Your personal AI assistant")

    st.divider()

    st.subheader("Features")

    st.markdown("""
    - 💬 AI Conversations
    - 🧠 Long-term Memory
    - 📝 Task Management
    - 🔍 Memory Retrieval
    - 📚 Learning Assistance
    """)

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []
        st.session_state.chat_history = []

        st.rerun()

    st.caption("Type `help` to see available commands.")


# ==========================================
# 10. DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# 11. CHAT INPUT
# ==========================================

user_input = st.chat_input(
    "Message AI Agent..."
)


# ==========================================
# 12. PROCESS USER MESSAGE
# ==========================================

if user_input:

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):

        st.markdown(user_input)

    with st.chat_message("assistant"):

        try:

            # Check for built-in commands

            command_response = handle_command(user_input)

            if command_response is not None:

                response = command_response

            else:

                # Get saved memories

                memory_context = build_memory_context()

                # AI AGENT IDENTITY

                system_message = {
                    "role": "system",
                    "content": (
                        "You are AI Agent, a personal AI assistant "
                        "created as part of the Personal AI Assistant project. "

                        "IDENTITY: "
                        "Your official name is AI Agent. "
                        "You are a personal AI assistant powered by an "
                        "AI model accessed through Groq. "
                        "Your product name is AI Agent. "
                        "Never introduce yourself as ChatGPT. "
                        "Never claim that your product name is ChatGPT. "
                        "Be honest about your underlying AI technology. "

                        "PERSONALITY: "
                        "Be friendly, intelligent, professional and conversational. "
                        "Give clear and useful answers. "
                        "Explain complicated topics simply. "

                        "CAPABILITIES: "
                        "Help with questions, programming, learning, "
                        "memory management, task management and productivity. "

                        "INTRODUCTION: "
                        "If asked who you are, say: "
                        "'I am AI Agent, your personal AI assistant. "
                        "I can help you with conversations, learning, "
                        "memory storage and task management.' "

                        "\n\nSAVED MEMORIES:\n"
                        + memory_context
                    )
                }

                # Keep recent conversation context

                recent_messages = (
                    st.session_state.messages[-10:]
                )

                messages = (
                    [system_message]
                    + recent_messages
                    + [
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                )

                # Get AI response from Groq

                response = ask_agent(messages)

                # Save conversation context

                st.session_state.messages.extend([
                    {
                        "role": "user",
                        "content": user_input
                    },
                    {
                        "role": "assistant",
                        "content": response
                    }
                ])

            # Display response

            st.markdown(response)

        except Exception as error:

            response = (
                "Something went wrong while processing your request. "
                "Please check your API settings and try again."
            )

            st.error(response)

            print(
                "Application error:",
                type(error).__name__
            )

    # Save displayed conversation

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })


# ==========================================
# 13. FOOTER
# ==========================================

st.divider()

st.caption(
    "AI Agent | Powered by Groq | Personal AI Assistant"
)

