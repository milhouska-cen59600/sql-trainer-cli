from tasks import get_random_task

state = {
    "started": False,
    "difficulty": None,
    "type": None,
    "current_task": None,
    "step": "idle",
    "score_correct": 0,
    "score_total": 0,
}


def normalize_sql(text):
    return text.strip().rstrip(";").lower().split()


def check_write_query_answer(user_input, expected_answer):
    return normalize_sql(user_input) == normalize_sql(expected_answer)


def check_find_bug_answer(user_input, keywords):
    answer = user_input.lower()
    return any(keyword in answer for keyword in keywords)


def check_explain_result_answer(user_input, keywords):
    answer = user_input.lower()
    matches = sum(1 for keyword in keywords if keyword in answer)
    return matches >= 2


def check_answer(user_input, task):
    if task["type"] == "write-query":
        return check_write_query_answer(user_input, task["expected_answer"])

    if task["type"] == "find-bug":
        return check_find_bug_answer(user_input, task["keywords"])

    if task["type"] == "explain-result":
        return check_explain_result_answer(user_input, task["keywords"])

    return False


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
    print("assistant> /score - show current score")
    print("assistant> /exit - quit the application")
    print("assistant> When a task is shown, type your answer directly.")


def print_score():
    print(f"assistant> Score: {state['score_correct']}/{state['score_total']}")


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

    print("assistant> Type your answer or use /hint, /solution, /next, /score, or /exit")


def handle_task_answer(user_input):
    task = state["current_task"]

    if not task:
        print("assistant> No active task. Type /start first.")
        return True

    state["score_total"] += 1

    is_correct = check_answer(user_input, task)

    if is_correct:
        state["score_correct"] += 1
        print("assistant> Correct!")
    else:
        print("assistant> Not quite.")
        print(f"assistant> Expected: {task['expected_answer']}")

    print_score()
    print("assistant> Type /next for another task or /solution to review the full solution.")
    return True


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

    if user_input == "/score":
        print_score()
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

    if state["step"] == "task":
        return handle_task_answer(user_input)

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