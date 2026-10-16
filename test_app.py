import unittest
from unittest.mock import patch

import app
from tasks import TASKS


class SQLNormalizationTests(unittest.TestCase):
    def test_gui_tokenization(self):
        self.assertEqual(
            app.normalize_sql(" SELECT name,balance FROM accounts WHERE balance>=1000; "),
            ["select", "name", ",", "balance", "from", "accounts",
             "where", "balance", ">=", "1000"],
        )
        self.assertEqual(
            app.normalize_sql("SELECT 'O''Brien', 10.50 FROM customers;"),
            ["select", "'O''Brien'", ",", "10.50", "from", "customers"],
        )

    def test_both_sql_task_types_accept_formatting_not_literal_changes(self):
        for task_type in ("write-query", "find-bug"):
            task = {
                "type": task_type,
                "expected_answer": "SELECT name, city FROM customers WHERE name = 'O''Brien';",
            }
            with self.subTest(task_type=task_type):
                self.assertTrue(app.check_answer(
                    "select name,city\nfrom customers where name='O''Brien'", task,
                ))
                self.assertFalse(app.check_answer(
                    "select name,city from customers where name='o''brien';", task,
                ))
                self.assertFalse(app.check_answer(
                    "select name,city from customers where name='O'' Brien';", task,
                ))
                self.assertFalse(app.check_answer(task["expected_answer"] + ";", task))


class CLIScoringTests(unittest.TestCase):
    def setUp(self):
        state_patch = patch.dict(app.state, {
            "started": False, "difficulty": "beginner", "type": "write-query",
            "current_task": None, "answered_current_task": False, "step": "idle",
            "score_correct": 0, "score_total": 0,
        }, clear=True)
        state_patch.start()
        self.addCleanup(state_patch.stop)
        print_patch = patch("builtins.print")
        self.output = print_patch.start()
        self.addCleanup(print_patch.stop)
        self.task = next(task for task in TASKS if task["id"] == 2)
        selection = patch("app.get_random_task", return_value=self.task)
        self.selection = selection.start()
        self.addCleanup(selection.stop)

    def test_only_first_answer_counts_for_each_task_type(self):
        for task_type in ("write-query", "find-bug", "explain-result"):
            self.selection.return_value = next(task for task in TASKS if task["type"] == task_type)
            for first_correct in (True, False):
                with self.subTest(task_type=task_type, first_correct=first_correct):
                    app.state.update(score_correct=0, score_total=0)
                    app.show_task()
                    correct = app.state["current_task"]["expected_answer"]
                    app.handle_command(correct if first_correct else "wrong")
                    app.handle_command(correct)
                    app.handle_task_answer("wrong")
                    self.assertEqual(app.state["score_total"], 1)
                    self.assertEqual(app.state["score_correct"], int(first_correct))
                    self.assertTrue(app.state["answered_current_task"])

    def test_next_resets_guard_even_when_same_catalog_task_is_selected(self):
        app.show_task()
        for total in (1, 2):
            app.handle_command(self.task["expected_answer"])
            self.assertEqual(app.state["score_total"], total)
            self.assertEqual(app.state["score_correct"], total)
            app.handle_command("/solution")
            app.handle_command("/hint")
            app.handle_command("/score")
            app.handle_command(self.task["expected_answer"])
            self.assertEqual(app.state["score_total"], total)
            app.handle_command("/next")
            self.assertFalse(app.state["answered_current_task"])

    def test_start_resets_guard_and_new_task_can_be_scored(self):
        app.show_task()
        app.handle_command(self.task["expected_answer"])
        app.handle_command("/start")
        self.assertIsNone(app.state["current_task"])
        self.assertFalse(app.state["answered_current_task"])
        app.handle_command("beginner")
        app.handle_command("write-query")
        app.handle_command(self.task["expected_answer"])
        self.assertEqual(app.state["score_total"], 2)
        self.assertEqual(app.state["score_correct"], 2)

    def test_blank_answer_does_not_consume_attempt(self):
        app.show_task()
        app.handle_command("  ")
        self.assertFalse(app.state["answered_current_task"])
        self.assertEqual(app.state["score_total"], 0)
        app.handle_command(self.task["expected_answer"])
        self.assertEqual(app.state["score_correct"], 1)

    def test_missing_task_clears_previous_task_and_does_not_score(self):
        app.show_task()
        self.selection.return_value = None
        app.handle_command("/next")
        self.assertIsNone(app.state["current_task"])
        app.handle_task_answer(self.task["expected_answer"])
        self.assertEqual(app.state["score_total"], 0)


if __name__ == "__main__":
    unittest.main()
