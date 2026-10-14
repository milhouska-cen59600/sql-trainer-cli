from tasks import get_random_task

state = {
    "started": False,
    "difficulty": None,
    "type": None,
    "current_task": None,
    "step": "idle",
}


def print_welcome():
    print("assistant> Welcome to SQL Trainer CLI")
    print("assistant> Type /start to begin or /help for commands")


def print_help():
    print("assistant> Available commands:")
    print("assistant> /start - begin a new task flow")
    print("assistant> /help - show available commands")
    print("assistant> /hint - show a hint for the current task")
    print("assistant> /solution - show the solution")
    print("assistant> /next - generate another task with current settings")
    print("assistant> /exit - quit the application")


def ask_difficulty():
    state["step"] = "difficulty"
    print("assistant> Choose difficulty: beginner, intermediate, advanced")


def ask_type():
    state["step"] = "type"
    print("assistant> Choose task type: write-query, find-bug, explain-result")


def show_task():
    task = get_random_task(state["difficulty"], state["type"])

    if not task:
        print("assistant> No task found for this difficulty and type.")
        print("assistant> Try /start to choose again.")
        state["step"] = "idle"
        return

    state["current_task"] = task
    state["step"] = "task"

    print("assistant> Task:")
    print(f"assistant> {task['prompt']}")

    if task["sql"]:
        print("assistant> SQL:")
        print(task["sql"])

    print("assistant> Type /hint, /solution, /next, or /exit")


def handle_command(user_input):
    if user_input == "/help":
        print_help()
        return True

    if user_input == "/exit":
        print("assistant> Goodbye!")
        return False

    if user_input == "/start":
        state["started"] = True
        state["current_task"] = None
        ask_difficulty()
        return True

    if user_input == "/hint":
        if not state["current_task"]:
            print("assistant> No active task. Type /start first.")
            return True

        print(f"assistant> Hint: {state['current_task']['hint']}")
        return True

    if user_input == "/solution":
        if not state["current_task"]:
            print("assistant> No active task. Type /start first.")
            return True

        print(f"assistant> Solution: {state['current_task']['solution']}")
        return True

    if user_input == "/next":
        if not state["difficulty"] or not state["type"]:
            print("assistant> Start first with /start.")
            return True

        show_task()
        return True

    if state["step"] == "difficulty":
        if user_input in ["beginner", "intermediate", "advanced"]:
            state["difficulty"] = user_input
            ask_type()
        else:
            print("assistant> Invalid difficulty. Choose: beginner, intermediate, advanced")
        return True

    if state["step"] == "type":
        if user_input in ["write-query", "find-bug", "explain-result"]:
            state["type"] = user_input
            show_task()
        else:
            print("assistant> Invalid task type. Choose: write-query, find-bug, explain-result")
        return True

    print("assistant> Unknown input. Type /help for commands.")
    return True


def main():
    print_welcome()

    running = True
    while running:
        user_input = input("you> ").strip()
        running = handle_command(user_input)


if __name__ == "__main__":
    main()