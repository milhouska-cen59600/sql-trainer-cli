import tkinter as tk
import unittest
from collections import Counter
from unittest.mock import patch

from gui_app import (
    ANSWER_LABELS,
    DIFFICULTY_LABELS,
    TASK_TYPE_LABELS,
    SQLTrainerGUI,
)
from tasks import TASKS, generate_tasks, get_random_task


class SQLTrainerGUITests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.app = SQLTrainerGUI(self.root)

    def select_task(self, difficulty="beginner", task_type="write-query"):
        self.app.difficulty_var.set(DIFFICULTY_LABELS[difficulty])
        self.app.type_var.set(TASK_TYPE_LABELS[task_type])
        self.app.start_task()

    def answer(self, text):
        self.app.answer_text.delete("1.0", tk.END)
        self.app.answer_text.insert("1.0", text)
        self.app.check_answer()

    def feedback(self):
        return self.app.feedback_text.get("1.0", "end-1c")

    def test_all_levels_offer_three_task_types(self):
        self.assertEqual(
            self.app.difficulty_box["values"],
            ("Junior", "Medior", "Senior"),
        )
        expected_types = set(TASK_TYPE_LABELS.values())

        for difficulty in DIFFICULTY_LABELS:
            with self.subTest(difficulty=difficulty):
                self.app.difficulty_var.set(
                    DIFFICULTY_LABELS[difficulty]
                )
                self.assertEqual(
                    set(self.app.type_box["values"]),
                    expected_types,
                )

    def test_every_combination_loads_correct_task(self):
        for difficulty in DIFFICULTY_LABELS:
            for task_type in TASK_TYPE_LABELS:
                with self.subTest(
                    difficulty=difficulty,
                    task_type=task_type,
                ):
                    self.select_task(difficulty, task_type)
                    task = self.app.current_task

                    self.assertIsNotNone(task)
                    self.assertEqual(task["difficulty"], difficulty)
                    self.assertEqual(task["type"], task_type)

                    self.app.next_button.invoke()
                    self.assertEqual(
                        self.app.current_task["difficulty"],
                        difficulty,
                    )
                    self.assertEqual(
                        self.app.current_task["type"],
                        task_type,
                    )

    def test_available_type_is_preserved_between_levels(self):
        self.app.type_var.set(TASK_TYPE_LABELS["find-bug"])
        self.app.difficulty_var.set(DIFFICULTY_LABELS["advanced"])

        self.assertEqual(
            self.app.type_var.get(),
            TASK_TYPE_LABELS["find-bug"],
        )

    def test_unavailable_type_is_replaced(self):
        catalog = [
            {"difficulty": "beginner", "type": "write-query"},
            {"difficulty": "advanced", "type": "find-bug"},
        ]
        with patch("gui_app.TASKS", catalog):
            app = SQLTrainerGUI(self.root)
            app.difficulty_var.set(DIFFICULTY_LABELS["advanced"])

            self.assertEqual(
                app.type_var.get(),
                TASK_TYPE_LABELS["find-bug"],
            )

    def test_empty_catalog_disables_loading(self):
        with patch("gui_app.TASKS", []):
            app = SQLTrainerGUI(self.root)

            self.assertEqual(app.difficulty_var.get(), "")
            self.assertEqual(app.type_var.get(), "")

            for widget in (
                app.difficulty_box,
                app.type_box,
                app.start_button,
                app.next_button,
            ):
                self.assertTrue(widget.instate(["disabled"]))

            self.assertEqual(
                app.feedback_text.get("1.0", "end-1c"),
                "Nejsou k dispozici žádné úlohy.",
            )

    def test_score_counts_answer_only_once(self):
        self.select_task()
        self.app.show_hint()
        self.assertEqual(self.app.score_total, 0)

        self.answer(self.app.current_task["expected_answer"])
        self.assertEqual(
            (self.app.score_correct, self.app.score_total),
            (1, 1),
        )

        self.app.check_answer()
        self.assertEqual(
            (self.app.score_correct, self.app.score_total),
            (1, 1),
        )

        self.app.next_task()
        self.answer("nesprávná odpověď")
        self.assertEqual(
            (self.app.score_correct, self.app.score_total),
            (1, 2),
        )

    def test_reset_score(self):
        self.app.score_correct = 2
        self.app.score_total = 3
        self.app.update_score_label()

        self.app.reset_score_button.invoke()

        self.assertEqual(
            (self.app.score_correct, self.app.score_total),
            (0, 0),
        )
        self.assertEqual(
            self.app.score_label.cget("text"),
            "Skóre: 0/0",
        )
        self.assertEqual(
            self.feedback(),
            "Skóre bylo vynulováno.",
        )

    def test_empty_answer_and_shown_solution_do_not_award_score(self):
        self.select_task()
        self.app.check_answer()

        self.assertFalse(self.app.answered_current_task)
        self.assertEqual(self.app.score_total, 0)

        self.app.show_solution()
        self.answer(self.app.current_task["expected_answer"])

        self.assertTrue(self.app.answered_current_task)
        self.assertEqual(
            (self.app.score_correct, self.app.score_total),
            (0, 0),
        )

        self.app.next_task()
        self.assertFalse(self.app.solution_shown)
        self.assertFalse(self.app.answered_current_task)

    def test_sql_matching_rules(self):
        self.assertTrue(
            self.app.check_write_query_answer(
                " SELECT * FROM klienti ; ",
                "select * from klienti",
            )
        )
        self.assertTrue(
            self.app.check_write_query_answer(
                "SELECT id,jmeno FROM klienti",
                "SELECT id, jmeno FROM klienti;",
            )
        )
        self.assertFalse(
            self.app.check_write_query_answer(
                "SELECT jmeno FROM klienti",
                "SELECT * FROM klienti",
            )
        )
        self.assertFalse(
            self.app.check_find_bug_answer(
                "SELECT jmeno FROM klienti WHERE mesto = Praha;",
                "SELECT jmeno FROM klienti WHERE mesto = 'Praha';",
            )
        )

    def test_sql_matching_preserves_string_values(self):
        self.assertFalse(
            self.app.check_write_query_answer(
                "SELECT * FROM klienti WHERE mesto = 'praha';",
                "SELECT * FROM klienti WHERE mesto = 'Praha';",
            )
        )
        self.assertFalse(
            self.app.check_write_query_answer(
                "SELECT * FROM klienti WHERE jmeno = 'Jan Novak';",
                "SELECT * FROM klienti WHERE jmeno = 'Jan  Novak';",
            )
        )

    def test_explanation_requires_all_keywords(self):
        self.assertTrue(
            self.app.check_explain_result_answer(
                "Pro každý typ vrátí součet částek.",
                ["typ", "součet"],
            )
        )
        self.assertFalse(
            self.app.check_explain_result_answer(
                "Vrátí typ transakce.",
                ["typ", "součet"],
            )
        )

    def test_find_bug_prefills_editor(self):
        for difficulty in DIFFICULTY_LABELS:
            with self.subTest(difficulty=difficulty):
                self.select_task(difficulty, "find-bug")
                task = self.app.current_task

                self.assertEqual(
                    self.app.answer_text.get("1.0", "end-1c"),
                    task["sql"],
                )
                self.assertFalse(
                    self.app.is_correct_answer(task["sql"], task)
                )

    def test_corrected_sql_awards_score(self):
        self.select_task("advanced", "find-bug")
        self.answer(self.app.current_task["expected_answer"])

        self.assertEqual(
            (self.app.score_correct, self.app.score_total),
            (1, 1),
        )

    def test_labels_and_task_text_follow_task_type(self):
        for task_type in TASK_TYPE_LABELS:
            with self.subTest(task_type=task_type):
                self.select_task(task_type=task_type)

                self.assertEqual(
                    self.app.answer_label.cget("text"),
                    ANSWER_LABELS[task_type],
                )
                self.assertEqual(
                    self.app.task_text.get("1.0", "end-1c"),
                    self.app.current_task["prompt"],
                )
                self.assertEqual(
                    self.app.task_text.cget("state"),
                    "disabled",
                )

                expected_manager = (
                    "" if task_type == "write-query" else "grid"
                )
                self.assertEqual(
                    self.app.sql_heading.winfo_manager(),
                    expected_manager,
                )

    def test_write_query_clears_previous_sql(self):
        self.select_task(task_type="find-bug")
        self.select_task(task_type="write-query")

        self.assertEqual(
            self.app.answer_text.get("1.0", "end-1c"),
            "",
        )

    def test_buttons_have_czech_labels(self):
        expected = (
            (self.app.start_button, "Spustit"),
            (self.app.check_button, "Zkontrolovat"),
            (self.app.hint_button, "Nápověda"),
            (self.app.solution_button, "Řešení"),
            (self.app.next_button, "Další úloha"),
            (self.app.reset_score_button, "Vynulovat skóre"),
        )
        for button, text in expected:
            with self.subTest(text=text):
                self.assertEqual(button.cget("text"), text)

    def test_actions_without_task_show_message(self):
        for action in (
            self.app.show_hint,
            self.app.show_solution,
            self.app.check_answer,
        ):
            action()
            self.assertEqual(
                self.feedback(),
                "Není načtená žádná úloha. "
                "Nejprve klikni na Spustit.",
            )

    def test_feedback_is_readonly_and_scrollable(self):
        self.select_task("advanced", "find-bug")
        message = "Řešení: " + "Dlouhé vysvětlení SQL. " * 300
        self.app.set_feedback(message)

        self.assertEqual(self.feedback(), message)
        self.assertEqual(
            self.app.feedback_text.cget("state"),
            "disabled",
        )

        self.app.feedback_text.insert("1.0", "nechtěná změna")
        self.assertEqual(self.feedback(), message)

        self.root.deiconify()
        for size in ("660x560", "960x800", "1100x850"):
            with self.subTest(size=size):
                self.root.geometry(size)
                self.root.update()

                self.assertGreaterEqual(
                    self.app.answer_text.winfo_height(), 40
                )
                self.assertGreaterEqual(
                    self.app.feedback_text.winfo_height(), 40
                )
                self.assertLessEqual(
                    self.app.feedback_text.winfo_rooty()
                    + self.app.feedback_text.winfo_height(),
                    self.root.winfo_rooty()
                    + self.root.winfo_height(),
                )

                self.app.feedback_text.yview_moveto(1)
                self.assertGreater(
                    self.app.feedback_text.yview()[0], 0
                )

    def test_missing_task_clears_editor(self):
        self.select_task(task_type="find-bug")

        with patch("gui_app.get_random_task", return_value=None):
            self.app.next_task()

        self.assertIsNone(self.app.current_task)
        self.assertEqual(
            self.app.answer_text.get("1.0", "end-1c"), ""
        )
        self.assertFalse(self.app.answered_current_task)

    def test_catalog_has_three_tasks_per_combination(self):
        counts = Counter(
            (task["difficulty"], task["type"])
            for task in TASKS
        )
        self.assertEqual(len(TASKS), 27)

        for difficulty in DIFFICULTY_LABELS:
            for task_type in TASK_TYPE_LABELS:
                self.assertEqual(
                    counts[(difficulty, task_type)], 3
                )

    def test_catalog_fields_and_expected_answers(self):
        required = {
            "id",
            "difficulty",
            "type",
            "prompt",
            "sql",
            "hint",
            "solution",
            "expected_answer",
            "keywords",
        }
        self.assertEqual(
            len({task["id"] for task in TASKS}),
            len(TASKS),
        )

        for task in TASKS:
            with self.subTest(task_id=task["id"]):
                self.assertTrue(required.issubset(task))
                self.assertIn("Tabulka:", task["prompt"])
                self.assertIn("Sloupce:", task["prompt"])
                self.assertTrue(
                    self.app.is_correct_answer(
                        task["expected_answer"], task
                    )
                )

                if task["type"] == "find-bug":
                    self.assertFalse(
                        self.app.is_correct_answer(
                            task["sql"], task
                        )
                    )

    def test_generator_returns_fresh_catalog(self):
        first = generate_tasks()
        second = generate_tasks()

        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        self.assertIsNot(first[0], second[0])

        first[0]["prompt"] = "změněné zadání"
        self.assertNotEqual(
            first[0]["prompt"], second[0]["prompt"]
        )

    def test_random_selection_respects_filters(self):
        for difficulty in DIFFICULTY_LABELS:
            for task_type in TASK_TYPE_LABELS:
                task = get_random_task(difficulty, task_type)
                self.assertIsNotNone(task)
                self.assertEqual(task["difficulty"], difficulty)
                self.assertEqual(task["type"], task_type)

    def test_unknown_combination_returns_none(self):
        self.assertIsNone(
            get_random_task("neexistující", "write-query")
        )


if __name__ == "__main__":
    unittest.main()