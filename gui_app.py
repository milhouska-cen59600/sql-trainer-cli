import tkinter as tk
from tkinter import ttk
from tasks import get_random_task


class SQLTrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Trainer")
        self.root.geometry("800x600")

        self.current_task = None
        self.current_difficulty = "beginner"
        self.current_type = "write-query"
        self.score_correct = 0
        self.score_total = 0
        self.answered_current_task = False
        self.solution_shown = False

        self.build_ui()
        self.update_score_label()
        self.show_welcome()

    def build_ui(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill="x")

        ttk.Label(top_frame, text="Difficulty:").pack(side="left")
        self.difficulty_var = tk.StringVar(value="beginner")
        difficulty_box = ttk.Combobox(
            top_frame,
            textvariable=self.difficulty_var,
            values=["beginner", "intermediate", "advanced"],
            state="readonly",
            width=15,
        )
        difficulty_box.pack(side="left", padx=5)

        ttk.Label(top_frame, text="Task type:").pack(side="left", padx=(10, 0))
        self.type_var = tk.StringVar(value="write-query")
        type_box = ttk.Combobox(
            top_frame,
            textvariable=self.type_var,
            values=["write-query", "find-bug", "explain-result"],
            state="readonly",
            width=18,
        )
        type_box.pack(side="left", padx=5)

        self.score_label = ttk.Label(top_frame, text="Score: 0/0")
        self.score_label.pack(side="right")

        content_frame = ttk.Frame(self.root, padding=10)
        content_frame.pack(fill="both", expand=True)

        ttk.Label(content_frame, text="Task:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.task_label = tk.Label(
            content_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=760,
            font=("Arial", 11),
        )
        self.task_label.pack(fill="x", pady=(0, 10))

        ttk.Label(content_frame, text="SQL:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.sql_label = tk.Label(
            content_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=760,
            bg="#f4f4f4",
            relief="solid",
            padx=10,
            pady=10,
            font=("Courier New", 10),
        )
        self.sql_label.pack(fill="x", pady=(0, 10))

        ttk.Label(content_frame, text="Your answer:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.answer_text = tk.Text(content_frame, height=8, font=("Courier New", 10))
        self.answer_text.pack(fill="both", expand=False, pady=(0, 10))

        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(button_frame, text="Start", command=self.start_task).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Check", command=self.check_answer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Hint", command=self.show_hint).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Solution", command=self.show_solution).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Next", command=self.next_task).pack(side="left", padx=5)

        ttk.Label(content_frame, text="Feedback:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.feedback_label = tk.Label(
            content_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=760,
            fg="blue",
            font=("Arial", 11),
        )
        self.feedback_label.pack(fill="x")

    def show_welcome(self):
        self.task_label.config(text="Welcome to SQL Trainer GUI. Choose difficulty and task type, then click Start.")
        self.sql_label.config(text="")
        self.feedback_label.config(text="")

    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.score_correct}/{self.score_total}")

    def normalize_sql(self, text):
        return text.strip().rstrip(";").lower().split()

    def check_write_query_answer(self, user_input, expected_answer):
        return self.normalize_sql(user_input) == self.normalize_sql(expected_answer)

    def check_find_bug_answer(self, user_input, keywords):
        answer = user_input.lower()
        return any(keyword in answer for keyword in keywords)

    def check_explain_result_answer(self, user_input, keywords):
        answer = user_input.lower()
        matches = sum(1 for keyword in keywords if keyword in answer)
        return matches >= 2

    def is_correct_answer(self, user_input, task):
        if task["type"] == "write-query":
            return self.check_write_query_answer(user_input, task["expected_answer"])
        if task["type"] == "find-bug":
            return self.check_find_bug_answer(user_input, task["keywords"])
        if task["type"] == "explain-result":
            return self.check_explain_result_answer(user_input, task["keywords"])
        return False

    def start_task(self):
        self.current_difficulty = self.difficulty_var.get()
        self.current_type = self.type_var.get()
        self.load_task()

    def next_task(self):
        self.current_difficulty = self.difficulty_var.get()
        self.current_type = self.type_var.get()
        self.load_task()

    def load_task(self):
        task = get_random_task(self.current_difficulty, self.current_type)

        if not task:
            self.current_task = None
            self.task_label.config(text="No task found for this difficulty and type.")
            self.sql_label.config(text="")
            self.feedback_label.config(text="Try a different combination.")
            return

        self.current_task = task
        self.answered_current_task = False
        self.solution_shown = False

        self.task_label.config(text=task["prompt"])
        self.sql_label.config(text=task["sql"] if task["sql"] else "")
        self.answer_text.delete("1.0", tk.END)
        self.feedback_label.config(text="Task loaded. Write your answer and click Check.", fg="blue")

    def show_hint(self):
        if not self.current_task:
            self.feedback_label.config(text="No active task. Click Start first.", fg="red")
            return

        self.feedback_label.config(text=f"Hint: {self.current_task['hint']}", fg="darkorange")

    def show_solution(self):
        if not self.current_task:
            self.feedback_label.config(text="No active task. Click Start first.", fg="red")
            return

        self.solution_shown = True
        self.feedback_label.config(text=f"Solution: {self.current_task['solution']}", fg="purple")

    def check_answer(self):
        if not self.current_task:
            self.feedback_label.config(text="No active task. Click Start first.", fg="red")
            return

        if self.answered_current_task:
            self.feedback_label.config(text="This task has already been answered. Click Next for another task.", fg="red")
            return

        user_input = self.answer_text.get("1.0", tk.END).strip()
        if not user_input:
            self.feedback_label.config(text="Please enter an answer first.", fg="red")
            return

        self.answered_current_task = True

        if not self.solution_shown:
            self.score_total += 1

            if self.is_correct_answer(user_input, self.current_task):
                self.score_correct += 1
                self.feedback_label.config(text="Correct! Great job.", fg="green")
            else:
                self.feedback_label.config(
                    text="Not quite. Try Next for another task or Solution to review the answer.",
                    fg="red",
                )
        else:
            self.feedback_label.config(
                text="Answer checked after viewing the solution. No score awarded for this task.",
                fg="brown",
            )

        self.update_score_label()


def main():
    root = tk.Tk()
    app = SQLTrainerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()