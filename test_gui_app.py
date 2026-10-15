import tkinter as tk
import unittest
from unittest.mock import patch

from gui_app import SQLTrainerGUI
from tasks import TASKS


class SQLTrainerGUITests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.addCleanup(self.root.destroy)
        self.app = SQLTrainerGUI(self.root)

    def select_task(self, difficulty="beginner", task_type="write-query"):
        self.app.difficulty_var.set(difficulty)
        self.app.type_var.set(task_type)
        self.app.start_task()

    def answer(self, text):
        self.app.answer_text.delete("1.0", tk.END)
        self.app.answer_text.insert("1.0", text)
        self.app.check_answer()

    def test_every_offered_combination_loads_a_task(self):
        self.assertEqual(
            set(self.app.difficulty_box["values"]),
            {task["difficulty"] for task in TASKS},
        )
        for difficulty in self.app.difficulty_box["values"]:
            self.app.difficulty_var.set(difficulty)
            self.assertEqual(
                set(self.app.type_box["values"]),
                {task["type"] for task in TASKS if task["difficulty"] == difficulty},
            )
            for task_type in self.app.type_box["values"]:
                with self.subTest(difficulty=difficulty, task_type=task_type):
                    self.app.type_var.set(task_type)
                    self.app.start_button.invoke()
                    self.assertIsNotNone(self.app.current_task)
                    self.assertEqual(self.app.current_task["difficulty"], difficulty)
                    self.assertEqual(self.app.current_task["type"], task_type)
                    self.app.next_button.invoke()
                    self.assertIsNotNone(self.app.current_task)

    def test_difficulty_change_replaces_unavailable_type(self):
        self.app.difficulty_var.set("intermediate")
        self.assertEqual(self.app.type_box["values"], ("explain-result",))
        self.assertEqual(self.app.type_var.get(), "explain-result")
        self.app.difficulty_var.set("beginner")
        self.assertIn(self.app.type_var.get(), self.app.type_box["values"])
        self.assertNotIn("explain-result", self.app.type_box["values"])
        self.assertNotIn("advanced", self.app.difficulty_box["values"])

    def test_available_type_is_preserved(self):
        self.app.type_var.set("find-bug")
        self.app.update_task_types()
        self.assertEqual(self.app.type_var.get(), "find-bug")

    def test_options_follow_task_data(self):
        with patch("gui_app.TASKS", [{"difficulty": "advanced", "type": "find-bug"}]):
            app = SQLTrainerGUI(self.root)
            self.assertEqual(app.difficulty_box["values"], ("advanced",))
            self.assertEqual(app.difficulty_var.get(), "advanced")
            self.assertEqual(app.type_box["values"], ("find-bug",))
            self.assertEqual(app.type_var.get(), "find-bug")

    def test_empty_catalog_disables_selection_and_task_loading(self):
        with patch("gui_app.TASKS", []):
            app = SQLTrainerGUI(self.root)
            self.assertEqual(app.difficulty_var.get(), "")
            self.assertEqual(app.type_var.get(), "")
            for widget in (app.difficulty_box, app.type_box, app.start_button, app.next_button):
                self.assertTrue(widget.instate(["disabled"]))
            self.assertEqual(app.feedback_text.get("1.0", "end-1c"), "No exercises available.")

    def test_score_counts_each_answer_once_and_hint_does_not_change_it(self):
        self.select_task()
        self.app.show_hint()
        self.answer(self.app.current_task["expected_answer"].upper())
        self.assertEqual((self.app.score_correct, self.app.score_total), (1, 1))
        self.app.check_answer()
        self.assertEqual((self.app.score_correct, self.app.score_total), (1, 1))
        self.app.next_task()
        self.answer("incorrect answer")
        self.assertEqual((self.app.score_correct, self.app.score_total), (1, 2))

    def test_solution_and_empty_answer_do_not_award_score(self):
        self.select_task()
        self.app.check_answer()
        self.assertFalse(self.app.answered_current_task)
        self.assertEqual(self.app.score_total, 0)
        self.app.show_solution()
        self.answer(self.app.current_task["expected_answer"])
        self.assertEqual((self.app.score_correct, self.app.score_total), (0, 0))
        self.assertTrue(self.app.answered_current_task)
        self.app.next_task()
        self.assertFalse(self.app.solution_shown)
        self.assertFalse(self.app.answered_current_task)

    def test_answer_matching_rules(self):
        self.assertTrue(self.app.check_write_query_answer(" SELECT * FROM users; ", "select * from users"))
        self.assertFalse(self.app.check_write_query_answer("SELECT name FROM users", "SELECT * FROM users"))
        self.assertTrue(self.app.check_find_bug_answer("Missing QUOTES", ["quote", "string"]))
        self.assertFalse(self.app.check_find_bug_answer("Missing column", ["quote", "string"]))
        self.assertTrue(self.app.check_explain_result_answer("Department count", ["department", "count", "group"]))
        self.assertFalse(self.app.check_explain_result_answer("Department", ["department", "count", "group"]))

    def test_feedback_is_readonly_and_scrollable(self):
        message = "Solution: " + "Long SQL explanation. " * 300
        self.app.set_feedback(message, "purple")
        self.assertEqual(self.app.feedback_text.get("1.0", "end-1c"), message)
        self.assertEqual(self.app.feedback_text["state"], "disabled")
        self.app.feedback_text.insert("1.0", "unwanted edit")
        self.assertEqual(self.app.feedback_text.get("1.0", "end-1c"), message)
        self.root.deiconify()
        for size in ("660x560", "860x700", "1100x850"):
            with self.subTest(size=size):
                self.root.geometry(size)
                self.root.update()
                self.assertGreaterEqual(self.app.answer_text.winfo_height(), 60)
                self.assertGreaterEqual(self.app.feedback_text.winfo_height(), 60)
                self.assertLessEqual(
                    self.app.feedback_text.winfo_rooty() + self.app.feedback_text.winfo_height(),
                    self.root.winfo_rooty() + self.root.winfo_height(),
                )
                self.app.feedback_text.yview_moveto(1)
                self.assertGreater(self.app.feedback_text.yview()[0], 0)


if __name__ == "__main__":
    unittest.main()