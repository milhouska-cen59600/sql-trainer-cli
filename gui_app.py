import tkinter as tk
from tkinter import ttk, scrolledtext
from tasks import TASKS, get_random_task


class SQLTrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Trainer")
        self.root.geometry("860x700")
        self.root.minsize(660, 560)

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
        top_frame = ttk.Frame(self.root, padding=(16, 12))
        top_frame.pack(fill="x")
        top_frame.columnconfigure(2, weight=1)

        ttk.Label(top_frame, text="Difficulty:").grid(row=0, column=0, sticky="w")
        self.difficulty_var = tk.StringVar(value="beginner")
        self.difficulty_box = ttk.Combobox(
            top_frame,
            textvariable=self.difficulty_var,
            values=list(dict.fromkeys(task["difficulty"] for task in TASKS)),
            state="readonly",
            width=15,
        )
        self.difficulty_box.grid(row=1, column=0, sticky="w", pady=(4, 0))

        ttk.Label(top_frame, text="Task type:").grid(row=0, column=1, sticky="w", padx=(16, 0))
        self.type_var = tk.StringVar(value="write-query")
        self.type_box = ttk.Combobox(
            top_frame,
            textvariable=self.type_var,
            state="readonly",
            width=18,
        )
        self.type_box.grid(row=1, column=1, sticky="w", padx=(16, 0), pady=(4, 0))

        self.score_label = ttk.Label(top_frame, text="Score: 0/0", font=("Segoe UI", 11, "bold"))
        self.score_label.grid(row=0, column=2, rowspan=2, sticky="e", padx=(16, 0))
        ttk.Separator(self.root).pack(fill="x")

        content_frame = ttk.Frame(self.root, padding=16)
        content_frame.pack(fill="both", expand=True)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(5, weight=3)
        content_frame.rowconfigure(8, weight=2)

        ttk.Label(content_frame, text="Task:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        self.task_label = tk.Label(
            content_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=620,
            font=("Segoe UI", 11),
        )
        self.task_label.grid(row=1, column=0, sticky="ew", pady=(4, 12))

        ttk.Label(content_frame, text="SQL:", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, sticky="w")
        self.sql_label = tk.Label(
            content_frame,
            text="",
            justify="left",
            anchor="w",
            wraplength=620,
            bg="#f4f4f4",
            relief="flat",
            padx=10,
            pady=10,
            font=("Courier New", 10),
        )
        self.sql_label.grid(row=3, column=0, sticky="ew", pady=(4, 12))
        content_frame.bind("<Configure>", self.update_wraplength)

        ttk.Label(content_frame, text="Your answer:", font=("Segoe UI", 11, "bold")).grid(row=4, column=0, sticky="w")
        self.answer_text = scrolledtext.ScrolledText(
            content_frame, height=6, width=1, wrap="word", font=("Courier New", 11),
            padx=10, pady=8, relief="solid", borderwidth=1, undo=True,
        )
        self.answer_text.grid(row=5, column=0, sticky="nsew", pady=(4, 12))

        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=6, column=0, sticky="ew", pady=(0, 12))

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_task)
        self.start_button.pack(side="left", padx=5)
        ttk.Button(button_frame, text="Check", command=self.check_answer).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Hint", command=self.show_hint).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Solution", command=self.show_solution).pack(side="left", padx=5)
        self.next_button = ttk.Button(button_frame, text="Next", command=self.next_task)
        self.next_button.pack(side="left", padx=5)
        ttk.Button(button_frame, text="Reset score", command=self.reset_score).pack(side="left", padx=5)

        ttk.Label(content_frame, text="Feedback:", font=("Segoe UI", 11, "bold")).grid(row=7, column=0, sticky="w")
        self.feedback_text = scrolledtext.ScrolledText(
            content_frame, height=5, width=1, wrap="word", state="disabled",
            font=("Segoe UI", 11), padx=10, pady=8, bg="#f4f4f4",
            relief="flat", borderwidth=0,
        )
        self.feedback_text.grid(row=8, column=0, sticky="nsew", pady=(4, 0))

        self.difficulty_var.trace_add("write", self.update_task_types)
        self.update_task_types()

    def update_task_types(self, *_args):
        difficulties = self.difficulty_box["values"]
        if difficulties and self.difficulty_var.get() not in difficulties:
            self.difficulty_var.set(difficulties[0])
            self.update_task_types()
            return
        if not difficulties:
            self.difficulty_var.set("")

        task_types = list(dict.fromkeys(
            task["type"] for task in TASKS
            if task["difficulty"] == self.difficulty_var.get()
        ))
        self.type_box.config(values=task_types)
        if self.type_var.get() not in task_types:
            self.type_var.set(task_types[0] if task_types else "")

        state = "normal" if task_types else "disabled"
        self.start_button.config(state=state)
        self.next_button.config(state=state)
        self.difficulty_box.config(state="readonly" if difficulties else "disabled")
        self.type_box.config(state="readonly" if task_types else "disabled")

    def update_wraplength(self, event):
        self.task_label.config(wraplength=max(1, event.width - 32))
        self.sql_label.config(wraplength=max(1, event.width - 52))

    def set_feedback(self, text, color="blue"):
        self.feedback_text.config(state="normal", fg=color)
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert("1.0", text)
        self.feedback_text.config(state="disabled")
        self.feedback_text.yview_moveto(0)

    def set_no_active_task_message(self):
        self.set_feedback("No active task. Click Start first.", "red")

    def show_welcome(self):
        self.task_label.config(text="Welcome to SQL Trainer GUI. Choose difficulty and task type, then click Start.")
        self.sql_label.config(text="")
        self.set_feedback("" if TASKS else "No exercises available.")

    def update_score_label(self):
        self.score_label.config(text=f"Score: {self.score_correct}/{self.score_total}")

    def reset_score(self):
        self.score_correct = 0
        self.score_total = 0
        self.update_score_label()
        self.set_feedback("Score has been reset.")

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
            self.set_feedback("Try a different combination.")
            return

        self.current_task = task
        self.answered_current_task = False
        self.solution_shown = False

        self.task_label.config(text=task["prompt"])
        self.sql_label.config(text=task["sql"] if task["sql"] else "")
        self.answer_text.delete("1.0", tk.END)
        self.set_feedback("Task loaded. Write your answer and click Check.")

    def show_hint(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return

        self.set_feedback(f"Hint: {self.current_task['hint']}", "#8a4b00")

    def show_solution(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return

        self.solution_shown = True
        self.set_feedback(f"Solution: {self.current_task['solution']}", "purple")

    def check_answer(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return

        if self.answered_current_task:
            self.set_feedback("This task has already been answered. Click Next for another task.", "red")
            return

        user_input = self.answer_text.get("1.0", tk.END).strip()
        if not user_input:
            self.set_feedback("Please enter an answer first.", "red")
            return

        self.answered_current_task = True

        if not self.solution_shown:
            self.score_total += 1

            if self.is_correct_answer(user_input, self.current_task):
                self.score_correct += 1
                self.set_feedback("Correct! Great job.", "green")
            else:
                self.set_feedback(
                    "Not quite. Try Next for another task or Solution to review the answer.",
                    "red",
                )
        else:
            self.set_feedback(
                "Answer checked after viewing the solution. No score awarded for this task.",
                "brown",
            )

        self.update_score_label()


def main():
    root = tk.Tk()
    app = SQLTrainerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()