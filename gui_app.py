import re
import tkinter as tk
from tkinter import font as tkfont

import customtkinter as ctk
import sqlparse

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

PAGE = "#EDF2F8"
NAVY = "#142033"
BLUE = "#2563EB"
TEXT = "#17263C"
EDITOR = "#142033"


def format_sql(text):
    """Upravi rozlozeni SQL; neoveruje ani neopravuje jeho logiku."""
    if not text.strip():
        return ""

    return sqlparse.format(
        text.strip(),
        reindent=True,
        indent_width=4,
        use_space_around_operators=True,
        keyword_case="upper",
    )


class ActionButton(ctk.CTkButton):
    def instate(self, states):
        disabled = self.cget("state") == "disabled"
        values = {
            "disabled": disabled,
            "!disabled": not disabled,
        }
        return all(values.get(state, False) for state in states)


class TrainerComboBox(ctk.CTkComboBox):
    def instate(self, states):
        disabled = self.cget("state") == "disabled"
        values = {
            "disabled": disabled,
            "!disabled": not disabled,
        }
        return all(values.get(state, False) for state in states)

    def current(self):
        values = list(self.cget("values"))
        current_value = self.get()
        try:
            return values.index(current_value)
        except ValueError:
            return -1


class Editor(ctk.CTkTextbox):
    TOKEN_PATTERN = re.compile(
        r"(?P<string>'(?:''|[^'])*')"
        r"|(?P<comment>--[^\n]*|/\*[\s\S]*?\*/)"
        r"|(?P<number>\b\d+(?:\.\d+)?\b)"
        r"|(?P<keyword>\b(?:"
        r"SELECT|FROM|WHERE|AND|OR|NOT|NULL|IS|AS|"
        r"JOIN|INNER|LEFT|RIGHT|FULL|OUTER|CROSS|ON|"
        r"GROUP|BY|HAVING|ORDER|ASC|DESC|DISTINCT|"
        r"CASE|WHEN|THEN|ELSE|END|WITH|EXISTS|IN|"
        r"BETWEEN|LIKE|UNION|ALL|OVER|PARTITION|"
        r"ROWS|RANGE|UNBOUNDED|PRECEDING|FOLLOWING|"
        r"CURRENT|ROW|NULLS|FIRST|LAST"
        r")\b)"
        r"|(?P<function>\b(?:"
        r"COUNT|SUM|AVG|MIN|MAX|ROW_NUMBER|RANK|DENSE_RANK|"
        r"LAG|LEAD|NVL|COALESCE|ROUND|TRUNC|TO_DATE|TO_CHAR|"
        r"REGEXP_LIKE|REGEXP_SUBSTR|REGEXP_REPLACE"
        r")\b)",
        re.IGNORECASE,
    )

    def __init__(self, master, *, sql=False, **kwargs):
        super().__init__(
            master,
            corner_radius=14,
            border_width=1,
            border_color="#D9E2EE" if not sql else "#263951",
            fg_color=EDITOR if sql else "#FFFFFF",
            text_color="#E3EBF7" if sql else TEXT,
            scrollbar_button_color="#415574" if sql else "#CBD5E1",
            scrollbar_button_hover_color="#5B7394",
            wrap="none" if sql else "word",
            width=1,
            height=1,
            undo=True,
            **kwargs,
        )
        self.sql_mode = sql

        colors = {
            "keyword": "#8CB7FF",
            "function": "#C5A3FF",
            "string": "#99DFB2",
            "number": "#F2C57C",
            "comment": "#8E9FB5",
        }
        for name, color in colors.items():
            self.tag_config(name, foreground=color)

        self.bind("<KeyRelease>", self._on_key_release, add="+")

    def edit_reset(self):
        self._textbox.edit_reset()

    def _on_key_release(self, _event):
        if self.sql_mode:
            self.highlight_sql()

    def highlight_sql(self):
        for name in (
            "keyword",
            "function",
            "string",
            "number",
            "comment",
        ):
            self.tag_remove(name, "1.0", "end")

        if not self.sql_mode:
            return

        text = self.get("1.0", "end-1c")
        for match in self.TOKEN_PATTERN.finditer(text):
            self.tag_add(
                match.lastgroup,
                f"1.0+{match.start()}c",
                f"1.0+{match.end()}c",
            )


class TaskEditor(Editor):
    SECTION_PATTERN = re.compile(
        r"^(?:Tabulka:.*|Vazba:|Vazby:)$",
        re.MULTILINE,
    )

    def __init__(self, master, accent_color, **kwargs):
        super().__init__(master, sql=False, **kwargs)
        self.configure(wrap="none")

        self.tag_config(
            "task_heading",
            foreground=accent_color,
            spacing1=4,
            spacing3=4,
        )
        self.tag_config(
            "task_instruction",
            foreground="#1E40AF",
            background="#EAF2FF",
            spacing1=3,
            spacing3=3,
        )
        self.tag_config(
            "schema_heading",
            foreground="#1D4ED8",
            spacing1=6,
            spacing3=3,
        )

    def apply_prompt_highlighting(self):
        for tag in (
            "task_heading",
            "task_instruction",
            "schema_heading",
        ):
            self.tag_remove(tag, "1.0", "end")

        text = self.get("1.0", "end-1c")
        if not text.strip():
            return

        task_match = re.search(
            r"^Úkol:[ \t]*$",
            text,
            re.MULTILINE,
        )

        if task_match:
            self.tag_add(
                "task_heading",
                f"1.0+{task_match.start()}c",
                f"1.0+{task_match.end()}c",
            )

            instruction_start = task_match.end()
            if text[instruction_start:instruction_start + 1] == "\n":
                instruction_start += 1

            remaining = text[instruction_start:]
            boundary = re.search(
                r"\n[ \t]*\n|(?m:^Tabulka:)",
                remaining,
            )
            instruction_end = (
                instruction_start + boundary.start()
                if boundary
                else len(text)
            )

            if instruction_end > instruction_start:
                self.tag_add(
                    "task_instruction",
                    f"1.0+{instruction_start}c",
                    f"1.0+{instruction_end}c",
                )
        else:
            for match in re.finditer(
                r"^Vysvětli[^\n]*",
                text,
                re.MULTILINE,
            ):
                self.tag_add(
                    "task_instruction",
                    f"1.0+{match.start()}c",
                    f"1.0+{match.end()}c",
                )

        for match in self.SECTION_PATTERN.finditer(text):
            self.tag_add(
                "schema_heading",
                f"1.0+{match.start()}c",
                f"1.0+{match.end()}c",
            )


class SQLTrainerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL trenažér – Oracle bankovní úlohy")
        self.root.geometry("1180x920")
        self.root.minsize(660, 560)
        self.root.configure(bg=PAGE)

        ctk.set_appearance_mode("light")

        available_fonts = set(tkfont.families(root))
        self.sql_font = next(
            (
                name
                for name in (
                    "Cascadia Code",
                    "Cascadia Mono",
                    "Consolas",
                    "DejaVu Sans Mono",
                )
                if name in available_fonts
            ),
            "Courier",
        )
        self.ui_font = (
            "Segoe UI" if "Segoe UI" in available_fonts else "Arial"
        )

        self.current_task = None
        self.current_difficulty = None
        self.current_type = None
        self.score_correct = 0
        self.score_total = 0
        self.answered_current_task = False
        self.solution_shown = False

        self.feedback_colors = {
            "info": ("#1E40AF", "#EFF6FF"),
            "success": ("#166534", "#ECFDF5"),
            "error": ("#991B1B", "#FEF2F2"),
            "warning": ("#854D0E", "#FFFBEB"),
            "solution": ("#6B21A8", "#FAF5FF"),
            "neutral": ("#334155", "#F1F5F9"),
        }

        self.build_ui()
        self.configure_responsive_layout()
        self.update_score_label()
        self.show_welcome()

    def label(self, parent, text, size=13, color=TEXT, **kwargs):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(self.ui_font, size, "bold"),
            text_color=color,
            anchor="w",
            **kwargs,
        )

    def build_ui(self):
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color=PAGE,
            corner_radius=0,
        )
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=12,
        )
        self.main_frame.columnconfigure(0, weight=1)

        header = ctk.CTkFrame(
            self.main_frame,
            fg_color=NAVY,
            corner_radius=16,
        )
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="SQL trenažér",
            font=(self.ui_font, 24, "bold"),
            text_color="#FFFFFF",
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=(10, 4),
        )

        ctk.CTkLabel(
            header,
            text="ORACLE • BANKOVNÍ ÚLOHY",
            font=(self.ui_font, 11, "bold"),
            text_color="#AFCBFF",
        ).grid(
            row=0,
            column=1,
            padx=18,
        )

        ctk.CTkLabel(
            header,
            text="Procvičování SQL dotazů, oprav chyb a vysvětlování výsledků.",
            font=(self.ui_font, 12),
            text_color="#D7E3F7",
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=18,
            pady=(0, 10),
        )

        controls = ctk.CTkFrame(
            self.main_frame,
            fg_color="#FFFFFF",
            corner_radius=14,
        )
        controls.grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(10, 0),
        )
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        self.label(controls, "Úroveň").grid(
            row=0, column=0, sticky="w", padx=14, pady=(8, 0)
        )
        self.label(controls, "Typ úlohy").grid(
            row=0, column=1, sticky="w", padx=10, pady=(8, 0)
        )

        self.difficulty_var = tk.StringVar(master=self.root)
        self.type_var = tk.StringVar(master=self.root)

        combo_options = {
            "state": "readonly",
            "height": 34,
            "corner_radius": 10,
            "fg_color": "#F1F5FA",
            "border_color": "#DCE5F0",
            "border_width": 1,
            "button_color": "#DCE7F5",
            "button_hover_color": "#C6D7ED",
            "text_color": TEXT,
            "font": (self.ui_font, 13),
            "dropdown_font": (self.ui_font, 13),
            "dropdown_fg_color": "#FFFFFF",
            "dropdown_text_color": TEXT,
            "dropdown_hover_color": "#E8F0FE",
        }

        self.difficulty_box = TrainerComboBox(
            controls,
            variable=self.difficulty_var,
            command=self.on_difficulty_change,
            **combo_options,
        )
        self.difficulty_box.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(14, 4),
            pady=(2, 12),
        )

        self.type_box = TrainerComboBox(
            controls,
            variable=self.type_var,
            **combo_options,
        )
        self.type_box.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=(2, 12),
        )

        self.score_label = ctk.CTkLabel(
            controls,
            text="Skóre: 0/0",
            fg_color="#E7EFFF",
            corner_radius=12,
            text_color="#1E40AF",
            font=(self.ui_font, 15, "bold"),
            width=130,
            height=38,
        )
        self.score_label.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(4, 14),
        )

        self.task_header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        self.task_header.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(8, 2),
        )
        self.task_header.columnconfigure(0, weight=1)

        self.label(
            self.task_header,
            "Zadání a popis tabulek",
            size=14,
        ).grid(row=0, column=0, sticky="w")

        self.task_hint_label = ctk.CTkLabel(
            self.task_header,
            text=(
                "Tip: horní blok je určen pro zadání, tabulky, vazby a ukázková data."
            ),
            font=(self.ui_font, 11),
            text_color="#64748B",
            anchor="e",
        )
        self.task_hint_label.grid(row=0, column=1, sticky="e")

        self.task_text = TaskEditor(
            self.main_frame,
            accent_color=BLUE,
            font=(self.sql_font, 14),
        )
        self.task_text.grid(row=3, column=0, sticky="nsew")

        self.sql_heading = self.label(
            self.main_frame,
            "SQL k úloze:",
            size=14,
        )
        self.sql_heading.grid(
            row=4, column=0, sticky="w", pady=(8, 2)
        )

        self.sql_label = Editor(
            self.main_frame,
            sql=True,
            font=(self.sql_font, 14),
        )
        self.sql_label.grid(row=5, column=0, sticky="nsew")

        answer_header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
            height=28,
        )
        answer_header.grid(
            row=6, column=0, sticky="ew", pady=(8, 2)
        )
        answer_header.columnconfigure(0, weight=1)

        self.answer_label = self.label(
            answer_header,
            "Tvá odpověď:",
            size=14,
        )
        self.answer_label.grid(row=0, column=0, sticky="w")

        self.format_button = ActionButton(
            answer_header,
            text="Formátovat SQL",
            command=self.format_answer,
            height=28,
            corner_radius=9,
            fg_color="#E0EAFE",
            hover_color="#CDDCFA",
            text_color="#1E40AF",
            font=(self.ui_font, 12, "bold"),
        )
        self.format_button.grid(row=0, column=1, sticky="e")

        self.answer_text = Editor(
            self.main_frame,
            sql=True,
            font=(self.sql_font, 14),
        )
        self.answer_text.grid(row=7, column=0, sticky="nsew")
        self.answer_text.bind(
            "<Control-Shift-F>",
            self.format_answer,
            add="+",
        )
        self.answer_text.bind(
            "<Control-Shift-f>",
            self.format_answer,
            add="+",
        )

        actions = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent",
        )
        actions.grid(
            row=8, column=0, sticky="ew", pady=(8, 0)
        )
        for column in range(3):
            actions.columnconfigure(
                column,
                weight=1,
                uniform="actions",
            )

        def button(text, command, primary=False):
            return ActionButton(
                actions,
                text=text,
                command=command,
                height=38,
                corner_radius=13,
                border_width=0,
                fg_color=BLUE if primary else "#DEE8F5",
                hover_color="#1D4ED8" if primary else "#CBD9ED",
                text_color="#FFFFFF" if primary else TEXT,
                font=(self.ui_font, 14, "bold"),
            )

        self.start_button = button(
            "Spustit", self.start_task, True
        )
        self.check_button = button(
            "Zkontrolovat", self.check_answer, True
        )
        self.next_button = button(
            "Další úloha", self.next_task
        )
        self.hint_button = button(
            "Nápověda", self.show_hint
        )
        self.solution_button = button(
            "Řešení", self.show_solution
        )
        self.reset_score_button = button(
            "Vynulovat skóre", self.reset_score
        )

        for index, widget in enumerate(
            (
                self.start_button,
                self.check_button,
                self.next_button,
                self.hint_button,
                self.solution_button,
                self.reset_score_button,
            )
        ):
            widget.grid(
                row=index // 3,
                column=index % 3,
                sticky="ew",
                padx=4,
                pady=3,
            )

        self.label(
            self.main_frame,
            "Zpětná vazba",
            size=14,
        ).grid(
            row=9, column=0, sticky="w", pady=(8, 2)
        )

        self.feedback_text = Editor(
            self.main_frame,
            font=(self.ui_font, 13),
        )
        self.feedback_text.grid(
            row=10, column=0, sticky="nsew"
        )

        self.difficulty_ids = list(
            dict.fromkeys(task["difficulty"] for task in TASKS)
        )
        names = [
            DIFFICULTY_LABELS.get(value, value)
            for value in self.difficulty_ids
        ]
        self.difficulty_box.configure(values=names)
        self.difficulty_var.set(names[0] if names else "")
        self._difficulty_trace_id = self.difficulty_var.trace_add(
            "write", self.update_task_types
        )
        self.update_task_types()

    def configure_responsive_layout(self):
        self.main_frame.rowconfigure(3, weight=6, minsize=50)
        self.main_frame.rowconfigure(5, weight=2, minsize=60)
        self.main_frame.rowconfigure(7, weight=3, minsize=60)
        self.main_frame.rowconfigure(10, weight=1, minsize=40)

        self.root.minsize(660, 560)
        self.main_frame.pack_configure(padx=10, pady=8)

        for widget in self.main_frame.grid_slaves():
            widget.grid_configure(pady=2)

        self.task_hint_label.grid_remove()

        header = self.main_frame.grid_slaves(row=0, column=0)[0]
        for widget in header.grid_slaves(row=1):
            widget.grid_remove()
        for widget in header.grid_slaves(row=0):
            widget.grid_configure(pady=6)

        controls = self.difficulty_box.master
        for widget in controls.grid_slaves():
            widget.grid_configure(pady=2)

        self.difficulty_box.configure(height=30)
        self.type_box.configure(height=30)
        self.score_label.configure(height=30)

        buttons = (
            self.start_button,
            self.check_button,
            self.next_button,
            self.hint_button,
            self.solution_button,
            self.reset_score_button,
        )
        for button in buttons:
            button.configure(height=30)
            button.grid_configure(pady=2)

    def on_difficulty_change(self, selected_value):
        if selected_value not in self.difficulty_box.cget("values"):
            return
        if self.difficulty_var.get() != selected_value:
            self.difficulty_var.set(selected_value)
        else:
            self.update_task_types()

    def update_task_types(self, *_args):
        names = list(self.difficulty_box.cget("values"))

        if not names:
            difficulty = None
        else:
            selected = self.difficulty_var.get()
            if selected not in names:
                return
            difficulty = self.difficulty_ids[names.index(selected)]

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
        self.type_box.configure(values=type_names)

        current_type = self.type_var.get()
        if current_type not in type_names:
            self.type_var.set(type_names[0] if type_names else "")

        self.difficulty_box.configure(
            state="readonly" if names else "disabled"
        )
        self.type_box.configure(
            state="readonly" if type_names else "disabled"
        )
        state = "normal" if type_names else "disabled"
        self.start_button.configure(state=state)
        self.next_button.configure(state=state)

    def set_readonly_text(self, widget, text):
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)

        if isinstance(widget, TaskEditor):
            widget.apply_prompt_highlighting()
        else:
            widget.highlight_sql()

        widget.configure(state="disabled")
        widget.yview_moveto(0)
        try:
            widget.xview_moveto(0)
        except Exception:
            pass

    def set_task_text(self, text):
        self.set_readonly_text(self.task_text, text)

    def set_sql_text(self, text):
        self.set_readonly_text(
            self.sql_label,
            format_sql(text),
        )

    def show_sql(self, visible):
        if visible:
            self.sql_heading.grid()
            self.sql_label.grid()
            self.main_frame.rowconfigure(
                5, weight=2, minsize=60
            )
        else:
            self.sql_heading.grid_remove()
            self.sql_label.grid_remove()
            self.main_frame.rowconfigure(
                5, weight=0, minsize=0
            )

    def set_feedback(self, text, level="info"):
        aliases = {
            "blue": "info",
            "green": "success",
            "red": "error",
            "purple": "solution",
            "brown": "warning",
        }
        level = aliases.get(level, level)
        foreground, background = self.feedback_colors.get(
            level,
            self.feedback_colors["info"],
        )
        self.feedback_text.configure(
            text_color=foreground,
            fg_color=background,
        )
        self.set_readonly_text(self.feedback_text, text)

    def show_welcome(self):
        self.set_task_text(
            "Vítej v Oracle SQL trenažéru.\n\n"
            "Úkol:\n"
            "Vyber úroveň a typ úlohy a klikni na Spustit.\n\n"
            "Tabulka: sample_table\n"
            "column_a | column_b\n"
            "---------+----------\n"
            "value_1  | value_2\n"
            "value_3  | value_4"
        )
        self.set_sql_text("")
        self.show_sql(False)
        self.set_feedback(
            "Připraveno. SQL můžeš upravit tlačítkem Formátovat SQL."
            if TASKS
            else "Nejsou k dispozici žádné úlohy."
        )

    def set_no_active_task_message(self):
        self.set_feedback(
            "Není načtená žádná úloha. Nejprve klikni na Spustit.",
            "error",
        )

    def update_score_label(self):
        self.score_label.configure(
            text=f"Skóre: {self.score_correct}/{self.score_total}"
        )

    def reset_score(self):
        self.score_correct = 0
        self.score_total = 0
        self.update_score_label()
        self.set_feedback(
            "Skóre bylo vynulováno.", "neutral"
        )

    def normalize_sql(self, text):
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
        if task["type"] in ("write-query", "find-bug"):
            return self.check_write_query_answer(
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
            self.set_feedback(
                "Vyber úroveň a typ úlohy.", "error"
            )
            return

        self.current_difficulty = self.difficulty_ids[
            difficulty_index
        ]
        self.current_type = self.task_type_ids[type_index]
        self.load_task()

    def next_task(self):
        self.start_task()

    def load_task(self):
        task = get_random_task(
            self.current_difficulty,
            self.current_type,
        )
        self.current_task = task
        self.answered_current_task = False
        self.solution_shown = False
        self.answer_text.delete("1.0", "end")

        if not task:
            self.set_task_text(
                "Pro tuto úroveň a typ nebyla nalezena žádná úloha."
            )
            self.set_sql_text("")
            self.show_sql(False)
            self.answer_label.configure(text="Tvá odpověď:")
            self.format_button.configure(state="disabled")
            self.answer_text.sql_mode = True
            self.answer_text.configure(
                font=(self.sql_font, 14)
            )
            self.answer_text.highlight_sql()
            self.answer_text.edit_reset()
            self.set_feedback(
                "Zkus jinou kombinaci.", "warning"
            )
            return

        task_type = task["type"]
        self.set_task_text(task["prompt"])
        self.answer_label.configure(
            text=ANSWER_LABELS.get(task_type, "Tvá odpověď:")
        )

        self.answer_text.sql_mode = (
            task_type != "explain-result"
        )
        self.answer_text.configure(
            font=(
                self.sql_font
                if self.answer_text.sql_mode
                else self.ui_font,
                14,
            )
        )
        self.format_button.configure(
            state="normal"
            if self.answer_text.sql_mode
            else "disabled"
        )

        sql = task.get("sql") or ""
        self.set_sql_text(sql)
        self.show_sql(bool(sql))

        if sql:
            if task_type == "explain-result":
                self.main_frame.rowconfigure(
                    5, weight=3, minsize=120
                )
            elif task_type == "find-bug":
                self.main_frame.rowconfigure(
                    5, weight=2, minsize=70
                )
            else:
                self.main_frame.rowconfigure(
                    5, weight=2, minsize=60
                )

        if sql:
            self.sql_heading.configure(
                text=(
                    "Původní SQL s chybou:"
                    if task_type == "find-bug"
                    else "SQL dotaz k vysvětlení:"
                )
            )

        if task_type == "find-bug":
            self.answer_text.insert(
                "1.0", format_sql(sql)
            )

        self.answer_text.highlight_sql()
        self.answer_text.edit_reset()
        self.answer_text.focus_set()

        if task_type == "explain-result":
            message = (
                "Vysvětli výsledek vlastními slovy.\n"
                "Kontrola zatím hledá klíčová slova."
            )
        else:
            message = (
                "Oprav SQL a klikni na Zkontrolovat."
                if task_type == "find-bug"
                else "Napiš SQL a klikni na Zkontrolovat."
            )
            message += (
                "\nFormátování: Ctrl+Shift+F. "
                "Kontrola zatím porovnává zápis, ne výsledky v databázi."
            )
        self.set_feedback(message)

    def format_answer(self, _event=None):
        if (
            not self.current_task
            or self.current_task["type"]
            == "explain-result"
        ):
            return "break"

        text = self.answer_text.get("1.0", "end-1c")
        if text.strip():
            self.answer_text._textbox.edit_separator()
            self.answer_text.delete("1.0", "end")
            self.answer_text.insert(
                "1.0", format_sql(text)
            )
            self.answer_text._textbox.edit_separator()
            self.answer_text.highlight_sql()

        return "break"

    def show_hint(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return
        self.set_feedback(
            f"Nápověda: {self.current_task['hint']}",
            "warning",
        )

    def show_solution(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return

        self.solution_shown = True
        solution = self.current_task["solution"]
        if self.current_task["type"] != "explain-result":
            solution = format_sql(solution)

        self.set_feedback(
            f"Řešení:\n{solution}",
            "solution",
        )

    def check_answer(self):
        if not self.current_task:
            self.set_no_active_task_message()
            return

        if self.answered_current_task:
            self.set_feedback(
                "Tato úloha už byla vyhodnocena. Klikni na Další úloha.",
                "error",
            )
            return

        answer = self.answer_text.get(
            "1.0", "end-1c"
        ).strip()
        if not answer:
            self.set_feedback(
                "Nejprve napiš odpověď.", "error"
            )
            return

        self.answered_current_task = True

        if self.solution_shown:
            self.set_feedback(
                "Řešení už bylo zobrazeno. "
                "Tato úloha se do skóre nezapočítává.",
                "neutral",
            )
        else:
            self.score_total += 1
            if self.is_correct_answer(
                answer, self.current_task
            ):
                self.score_correct += 1
                self.set_feedback(
                    "Odpověď odpovídá očekávanému řešení.",
                    "success",
                )
            else:
                self.set_feedback(
                    "Odpověď neodpovídá očekávanému řešení. "
                    "Klikni na Řešení pro porovnání "
                    "nebo na Další úloha.",
                    "error",
                )

        self.update_score_label()


def main():
    root = tk.Tk()
    SQLTrainerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()