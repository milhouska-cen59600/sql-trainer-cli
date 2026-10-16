import re
import tkinter as tk
from tkinter import scrolledtext, ttk

from tasks import TASKS, get_random_task


DIFFICULTY_LABELS = {
    "beginner": "Junior",
    "intermediate": "Medior",
    "advanced": "Senior",
}

TASK_TYPE_LABELS = {
    "write-query": "Napsat SQL dotaz",
    "find-bug": "Opravit chybu",
    "explain-result": "Vysvětlit výsledek",
}

ANSWER_LABELS = {
    "write-query": "Tvůj SQL dotaz:",
    "find-bug": "Oprav SQL dotaz:",
    "explain-result": "Tvé vysvětlení:",
}


class SQLTrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL trenažér – bankovní úlohy")
        self.root.geometry("960x800")
        self.root.minsize(660, 560)

        self.current_task = None
        self.current_difficulty = None
        self.current_type = None
        self.score_correct = 0
        self.score_total = 0
        self.answered_current_task = False
        self.solution_shown = False

        self.build_ui()
        self.update_score_label()
        self.show_welcome()

    def build_ui(self):
        top_frame = ttk.Frame(self.root, padding=(12, 8))
        top_frame.pack(fill="x")
        top_frame.columnconfigure(2, weight=1)

        ttk.Label(
            top_frame, text="Úroveň:"
        ).grid(row=0, column=0, sticky="w")

        self.difficulty_var = tk.StringVar()
        self.difficulty_box = ttk.Combobox(
            top_frame,
            textvariable=self.difficulty_var,
            state="readonly",
            width=18,
        )
        self.difficulty_box.grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )

        ttk.Label(
            top_frame, text="Typ úlohy:"
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))

        self.type_var = tk.StringVar()
        self.type_box = ttk.Combobox(
            top_frame,
            textvariable=self.type_var,
            state="readonly",
            width=22,
        )
        self.type_box.grid(
            row=1,
            column=1,
            sticky="w",
            padx=(12, 0),
            pady=(4, 0),
        )

        self.score_label = ttk.Label(
            top_frame,
            font=("Segoe UI", 11, "bold"),
        )
        self.score_label.grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
            padx=(12, 0),
        )

        ttk.Separator(self.root).pack(fill="x")

        content = ttk.Frame(self.root, padding=12)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(1, weight=2)
        content.rowconfigure(5, weight=3)
        content.rowconfigure(8, weight=2)

        ttk.Label(
            content,
            text="Zadání a popis tabulek:",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.task_text = scrolledtext.ScrolledText(
            content,
            height=7,
            width=1,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 11),
            padx=8,
            pady=6,
            bg="#f4f4f4",
            relief="flat",
        )
        self.task_text.grid(
            row=1, column=0, sticky="nsew", pady=(4, 8)
        )

        self.sql_heading = ttk.Label(
            content,
            text="SQL k úloze:",
            font=("Segoe UI", 11, "bold"),
        )
        self.sql_heading.grid(row=2, column=0, sticky="w")

        self.sql_label = tk.Label(
            content,
            text="",
            justify="left",
            anchor="w",
            wraplength=850,
            bg="#f4f4f4",
            padx=8,
            pady=6,
            font=("Courier New", 10),
        )
        self.sql_label.grid(
            row=3, column=0, sticky="ew", pady=(4, 8)
        )
        content.bind("<Configure>", self.update_wraplength)

        self.answer_label = ttk.Label(
            content,
            text="Tvá odpověď:",
            font=("Segoe UI", 11, "bold"),
        )
        self.answer_label.grid(row=4, column=0, sticky="w")

        self.answer_text = scrolledtext.ScrolledText(
            content,
            height=6,
            width=1,
            wrap="word",
            font=("Courier New", 11),
            padx=8,
            pady=6,
            relief="solid",
            borderwidth=1,
            undo=True,
        )
        self.answer_text.grid(
            row=5, column=0, sticky="nsew", pady=(4, 8)
        )

        button_frame = ttk.Frame(content)
        button_frame.grid(
            row=6, column=0, sticky="ew", pady=(0, 8)
        )

        for column in range(3):
            button_frame.columnconfigure(column, weight=1)

        self.start_button = ttk.Button(
            button_frame, text="Spustit", command=self.start_task
        )
        self.check_button = ttk.Button(
            button_frame,
            text="Zkontrolovat",
            command=self.check_answer,
        )
        self.hint_button = ttk.Button(
            button_frame, text="Nápověda", command=self.show_hint
        )
        self.solution_button = ttk.Button(
            button_frame, text="Řešení", command=self.show_solution
        )
        self.next_button = ttk.Button(
            button_frame, text="Další úloha", command=self.next_task
        )
        self.reset_score_button = ttk.Button(
            button_frame,
            text="Vynulovat skóre",
            command=self.reset_score,
        )

        buttons = (
            self.start_button,
            self.check_button,
            self.hint_button,
            self.solution_button,
            self.next_button,
            self.reset_score_button,
        )
        for index, button in enumerate(buttons):
            button.grid(
                row=index // 3,
                column=index % 3,
                sticky="ew",
                padx=3,
                pady=3,
            )

        ttk.Label(
            content,
            text="Zpětná vazba:",
            font=("Segoe UI", 11, "bold"),
        ).grid(row=7, column=0, sticky="w")

        self.feedback_text = scrolledtext.ScrolledText(
            content,
            height=4,
            width=1,
            wrap="word",
            state="disabled",
            font=("Segoe UI", 11),
            padx=8,
            pady=6,
            bg="#f4f4f4",
            relief="flat",
        )
        self.feedback_text.grid(
            row=8, column=0, sticky="nsew", pady=(4, 0)
        )

        self.difficulty_ids = list(
            dict.fromkeys(task["difficulty"] for task in TASKS)
        )
        names = [
            DIFFICULTY_LABELS.get(value, value)
            for value in self.difficulty_ids
        ]
        self.difficulty_box.config(values=names)
        self.difficulty_var.set(names[0] if names else "")
        self.difficulty_var.trace_add("write", self.update_task_types)
        self.update_task_types()

    def update_task_types(self, *_args):
        difficulty_names = list(self.difficulty_box["values"])

        if not difficulty_names:
            difficulty = None
        else:
            if self.difficulty_var.get() not in difficulty_names:
                self.difficulty_var.set(difficulty_names[0])
                return
            index = difficulty_names.index(self.difficulty_var.get())
            difficulty = self.difficulty_ids[index]

        self.task_type_ids = list(
            dict.fromkeys(
                task["type"]
                for task in TASKS
                if task["difficulty"] == difficulty
            )
        )
        type_names = [
            TASK_TYPE_LABELS.get(value, value)
            for value in self.task_type_ids
        ]
        self.type_box.config(values=type_names)

        if self.type_var.get() not in type_names:
            self.type_var.set(type_names[0] if type_names else "")

        self.difficulty_box.config(
            state="readonly" if difficulty_names else "disabled"
        )
        self.type_box.config(
            state="readonly" if type_names else "disabled"
        )
        state = "normal" if type_names else "disabled"
        self.start_button.config(state=state)
        self.next_button.config(state=state)

    def update_wraplength(self, event):
        self.sql_label.config(wraplength=max(1, event.width - 40))

    def set_task_text(self, text):
        self.task_text.config(state="normal")
        self.task_text.delete("1.0", tk.END)
        self.task_text.insert("1.0", text)
        self.task_text.config(state="disabled")
        self.task_text.yview_moveto(0)

    def set_feedback(self, text, color="blue"):
        self.feedback_text.config(state="normal", fg=color)
        self.feedback_text.delete("1.0", tk.END)
        self.feedback_text.insert("1.0", text)
        self.feedback_text.config(state="disabled")
        self.feedback_text.yview_moveto(0)

    def set_no_active_task_message(self):
        self.set_feedback(
            "Není načtená žádná úloha. Nejprve klikni na Spustit.",
            "red",
        )

    def show_welcome(self):
        self.set_task_text(
            "Vítej v SQL trenažéru s bankovními úlohami.\n\n"
            "Junior: základní výběr a filtrování.\n"
            "Medior: agregace, seskupování a HAVING.\n"
            "Senior: spojování tabulek a poddotazy.\n\n"
            "V každé úrovni můžeš napsat dotaz, opravit chybu "
            "nebo vysvětlit výsledek.\n"
            "Vyber úroveň a typ úlohy a klikni na Spustit."
        )
        self.sql_heading.grid_remove()
        self.sql_label.grid_remove()
        self.set_feedback(
            "Úlohy vznikají z místních šablon, nikoli pomocí AI."
            if TASKS
            else "Nejsou k dispozici žádné úlohy."
        )

    def update_score_label(self):
        self.score_label.config(
            text=f"Skóre: {self.score_correct}/{self.score_total}"
        )

    def reset_score(self):
        self.score_correct = 0
        self.score_total = 0
        self.update_score_label()
        self.set_feedback("Skóre bylo vynulováno.")

    def normalize_sql(self, text):
        # Zachováme obsah textových literálů, včetně velikosti písmen.
        tokens = re.findall(
            r"'(?:''|[^'])*'|[A-Za-z_][A-Za-z_0-9]*"
            r"|\d+(?:\.\d+)?|>=|<=|<>|!=|[^\s]",
            text.strip(),
        )
        if tokens and tokens[-1] == ";":
            tokens.pop()

        return [
            token if token.startswith("'") else token.lower()
            for token in tokens
        ]

    def check_write_query_answer(self, user_input, expected_answer):
        return (
            self.normalize_sql(user_input)
            == self.normalize_sql(expected_answer)
        )

    def check_find_bug_answer(self, user_input, expected_answer):
        return self.check_write_query_answer(
            user_input, expected_answer
        )

    def check_explain_result_answer(self, user_input, keywords):
        if not keywords:
            return False
        answer = user_input.casefold()
        return all(
            keyword.casefold() in answer
            for keyword in keywords
        )

    def is_correct_answer(self, user_input, task):
        if task["type"] == "write-query":
            return self.check_write_query_answer(
                user_input, task["expected_answer"]
            )
        if task["type"] == "find-bug":
            return self.check_find_bug_answer(
                user_input, task["expected_answer"]
            )
        if task["type"] == "explain-result":
            return self.check_explain_result_answer(
                user_input, task["keywords"]
            )
        return False

    def start_task(self):
        difficulty_index = self.difficulty_box.current()
        type_index = self.type_box.current()

        if difficulty_index < 0 or type_index < 0:
            self.set_feedback("Vyber úroveň a typ úlohy.", "red")
            return

        self.current_difficulty = self.difficulty_ids[difficulty_index]
        self.current_type = self.task_type_ids[type_index]
        self.load_task()

    def next_task(self):
        self.start_task()

    def load_task(self):
        task = get_random_task(
            self.current_difficulty, self.current_type
        )
        self.current_task = task
        self.answered_current_task = False
        self.solution_shown = False

        self.answer_text.delete("1.0", tk.END)
        self.answer_text.edit_reset()

        if not task:
            self.set_task_text(
                "Pro tuto úroveň a typ nebyla nalezena úloha."
            )
            self.sql_label.config(text="")
            self.sql_heading.grid_remove()
            self.sql_label.grid_remove()
            self.answer_label.config(text="Tvá odpověď:")
            self.set_feedback("Zkus jinou kombinaci.")
            return

        task_type = task["type"]
        self.set_task_text(task["prompt"])
        self.answer_label.config(
            text=ANSWER_LABELS.get(task_type, "Tvá odpověď:")
        )

        sql = task.get("sql")
        if sql:
            self.sql_heading.config(
                text=(
                    "Původní SQL s chybou:"
                    if task_type == "find-bug"
                    else "SQL dotaz k vysvětlení:"
                )
            )
            self.sql_label.config(text=sql)
            self.sql_heading.grid()
            self.sql_label.grid()
        else:
            self.sql_label.config(text="")
            self.sql_heading.grid_remove()
            self.sql_label.grid_remove()

        if task_type == "find-bug":
            self.answer_text.insert("1.0", sql or "")

        self.answer_text.edit_reset()
        self.answer_text.focus_set()

        if task_type == "explain-result":
            message = (
                "Vysvětli výsledek vlastními slovy a klikni "
                "na Zkontrolovat.\n"
                "Pozor: kontrola zatím pouze hledá klíčová slova, "
                "nerozumí významu celého vysvětlení."
            )
        else:
            message = (
                "Oprav předvyplněný dotaz."
                if task_type == "find-bug"
                else "Napiš SQL podle zadání."
            )
            message += (
                " Potom klikni na Zkontrolovat.\n"
                "Kontrola zatím porovnává zápis SQL; "
                "jiný rovnocenný zápis nemusí přijmout."
            )

        self.set_feedback(message)

    def show_hint(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return
        self.set_feedback(
            f"Nápověda: {self.current_task['hint']}",
            "#8a4b00",
        )

    def show_solution(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return
        self.solution_shown = True
        self.set_feedback(
            f"Řešení: {self.current_task['solution']}",
            "purple",
        )

    def check_answer(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return

        if self.answered_current_task:
            self.set_feedback(
                "Tato úloha už byla vyhodnocena. "
                "Klikni na Další úloha.",
                "red",
            )
            return

        answer = self.answer_text.get("1.0", tk.END).strip()
        if not answer:
            self.set_feedback("Nejprve napiš odpověď.", "red")
            return

        self.answered_current_task = True

        if self.solution_shown:
            self.set_feedback(
                "Řešení už bylo zobrazeno. "
                "Tato úloha se do skóre nezapočítává.",
                "brown",
            )
        else:
            self.score_total += 1

            if self.is_correct_answer(answer, self.current_task):
                self.score_correct += 1
                self.set_feedback(
                    "Odpověď odpovídá očekávanému řešení.",
                    "green",
                )
            else:
                self.set_feedback(
                    "Odpověď neodpovídá očekávanému řešení. "
                    "Klikni na Řešení pro porovnání "
                    "nebo na Další úloha.",
                    "red",
                )

        self.update_score_label()


def main():
    root = tk.Tk()
    SQLTrainerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()