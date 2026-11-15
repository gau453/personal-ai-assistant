
import re

from agent import ask_agent

from tools import (
    create_task_table,
    add_task,
    get_tasks,
    complete_task
)

from memory import (
    create_memory_table,
    save_memory,
    get_memory,
    get_all_memories,
    delete_memory
)


# =====================================
# INITIALIZE DATABASES
# =====================================

create_task_table()
create_memory_table()


# =====================================
# BUILD MEMORY CONTEXT
# =====================================

def build_memory_context():
    memories = get_all_memories()

    if not memories:
        return "No personal memories have been saved yet."

    context = "Here is what you know about the user:\n"

    for item in memories:
        context += f"- {item[1]}: {item[2]}\n"

    return context


# =====================================
# CONVERSATION HISTORY
# =====================================

messages = [
    {
        "role": "system",
        "content": """
        You are a helpful personal AI assistant.
        Help users with studying, planning and productivity.
        Be friendly, concise and useful.
        Use saved personal information when relevant.
        Never invent personal information.
        """
    }
]


# =====================================
# HANDLE USER COMMANDS
# =====================================

def handle_command(user_input):
    text = user_input.lower().strip()

    # HELP
    if text in ["help", "commands", "show commands"]:
        return """
Available commands:

MEMORY:
- Remember that I am learning Python
- Remember that my favourite language is Python
- Show my memories
- What am I learning?
- Forget my learning goal
- Forget my favourite language

TASKS:
- Add my task as learn Python
- Show tasks
- Complete task 1

AI:
- Ask any normal question!
"""

    # SHOW MEMORIES
    if any(phrase in text for phrase in [
        "show my memories",
        "show everything you remember",
        "what do you remember about me",
        "what do you know about me"
    ]):
        memories = get_all_memories()

        if not memories:
            return "I don't have any saved memories yet."

        return "\n".join(
            f"{item[1]}: {item[2]}"
            for item in memories
        )

    # REMEMBER LEARNING GOAL
    match = re.search(
        r"remember that i am learning (.+)",
        text
    )

    if match:
        value = match.group(1).strip().rstrip(".!?")
        return save_memory("learning", value)

    # REMEMBER PERSONAL INFORMATION
    match = re.search(
        r"remember that my (.+?) is (.+)",
        user_input,
        re.IGNORECASE
    )

    if match:
        key = match.group(1).strip().lower().replace(" ", "_")
        value = match.group(2).strip().rstrip(".!?")
        return save_memory(key, value)

    # RETRIEVE LEARNING GOAL
    if any(phrase in text for phrase in [
        "what am i learning",
        "which subject am i learning"
    ]):
        learning = get_memory("learning")

        if (
            not learning
            or "don't have that information" in str(learning).lower()
        ):
            return "I don't have your learning goal saved right now."

        return "You are learning " + str(learning[2])

    # FORGET LEARNING GOAL
    if text in ["forget my learning", "forget my learning goal"]:
        return delete_memory("learning")

    # FORGET OTHER PERSONAL INFORMATION
    match = re.search(r"forget my (.+)", text)

    if match:
        key = (
            match.group(1)
            .strip()
            .rstrip(".!?")
            .replace(" ", "_")
        )
        return delete_memory(key)

    # SHOW TASKS
    if any(phrase in text for phrase in [
        "show tasks",
        "list tasks",
        "my tasks",
        "view tasks"
    ]):
        tasks = get_tasks()

        if isinstance(tasks, str):
            return tasks

        if not tasks:
            return "You don't have any tasks yet."

        output = ["Here are your tasks:"]

        for task in tasks:
            status = "Completed" if task[2] else "Pending"
            output.append(f"{task[0]}. {task[1]} - {status}")

        return "\n".join(output)

    # COMPLETE TASK
    match = re.search(
        r"(?:complete|finish|done with|mark(?:\s+as)?"
        r"(?:\s+completed)?)\s+(?:the\s+)?"
        r"(?:task\s*)?#?(\d+)",
        text
    )

    if match:
        return complete_task(int(match.group(1)))

    # ADD TASK
    patterns = [
        r"(?:add|create|save)\s+(?:my\s+)?task\s+as\s+(.+)",
        r"(?:add|create|save)\s+(?:a\s+)?task\s+(?:to|:|-)\s*(.+)",
        r"(?:remind me to|remember to)\s+(.+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)

        if match:
            task = match.group(1).strip().rstrip(".!?")

            if task:
                return add_task(task)

    return None


# =====================================
# MAIN PROGRAM
# =====================================

print("\n===== PERSONAL AI AGENT =====")
print("Your personal assistant is ready!")
print("Type 'help' to see available commands.")
print("Type 'exit' to stop.\n")


while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("Agent: Goodbye!")
        break

    if not user_input:
        continue

    # CHECK MEMORY AND TASK COMMANDS
    try:
        result = handle_command(user_input)

    except Exception as error:
        print("\nAgent: I couldn't complete that command.")
        print("Error:", error, "\n")
        continue

    if result is not None:
        print("\nAgent:", result, "\n")

        messages.append({
            "role": "user",
            "content": user_input
        })

        messages.append({
            "role": "assistant",
            "content": str(result)
        })

        continue

    # NORMAL AI CONVERSATION
    messages.append({
        "role": "user",
        "content": user_input
    })

    try:
        memory_context = build_memory_context()

        messages[0]["content"] = f"""
        You are a helpful personal AI assistant.

        Help users with studying, planning and productivity.
        Be friendly, concise and useful.

        Use this saved personal information when relevant:

        {memory_context}

        Never invent personal information.
        """

        answer = ask_agent(messages)

        print("\nAgent:", answer, "\n")

        messages.append({
            "role": "assistant",
            "content": str(answer)
        })

    except Exception as error:
        print("\nAgent: Sorry, something went wrong.")
        print("Error:", error, "\n")
