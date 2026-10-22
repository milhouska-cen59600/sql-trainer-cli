import re
import sqlite3
import unittest
from collections import Counter
from unittest.mock import patch

from app import check_answer, check_explain_result_answer
from tasks import TASKS, _TABLES, _task, get_random_task


class TaskCatalogTests(unittest.TestCase):
    def test_contract_and_balanced_distribution(self):
        fields = {
            "id", "difficulty", "type", "prompt", "sql", "hint",
            "solution", "expected_answer", "keywords",
        }
        self.assertEqual(len({task["id"] for task in TASKS}), len(TASKS))
        self.assertEqual(
            Counter((task["difficulty"], task["type"]) for task in TASKS),
            Counter({
                (difficulty, task_type): 6
                for difficulty in ("beginner", "intermediate", "advanced")
                for task_type in ("write-query", "find-bug", "explain-result")
            }),
        )
        for task in TASKS:
            with self.subTest(task=task["id"]):
                self.assertEqual(set(task), fields)
                self.assertIsInstance(task["id"], int)
                self.assertTrue(task["prompt"].startswith("Úkol: "))
                self.assertTrue(task["hint"])
                self.assertEqual(task["expected_answer"], task["solution"])
                self.assertEqual(task["sql"] is None, task["type"] == "write-query")
                if task["type"] == "explain-result":
                    self.assertGreaterEqual(len(set(task["keywords"])), 2)
                else:
                    self.assertEqual(task["keywords"], [])

    def test_prompts_show_all_referenced_tables_with_two_aligned_rows(self):
        for task in TASKS:
            with self.subTest(task=task["id"]):
                sql = task["sql"] or task["solution"]
                referenced = set(re.findall(r"\b(?:FROM|JOIN)\s+(\w+)", sql))
                shown = set(re.findall(r"Tabulka: (\w+)", task["prompt"]))
                self.assertEqual(shown, referenced)
                for section in task["prompt"].split("Tabulka: ")[1:]:
                    lines = section.splitlines()
                    table = lines[0]
                    grid = lines[1:7]
                    self.assertEqual(len(grid), 6)
                    self.assertEqual(len({len(line) for line in grid}), 1)
                    for index in (0, 2, 5):
                        self.assertRegex(grid[index], r"^\+(?:-+\+)+$")
                    rows = [
                        tuple(cell.strip() for cell in grid[index].split("|")[1:-1])
                        for index in (1, 3, 4)
                    ]
                    # The final border immediately follows the two sample rows.
                    self.assertEqual(grid[5], grid[0])
                    self.assertEqual(rows[0], _TABLES[table][0])
                    self.assertEqual(
                        rows[1:],
                        [tuple(str(value) for value in row) for row in _TABLES[table][1]],
                    )

    def test_datatype_notes_match_displayed_schemas_for_all_tasks(self):
        for task in TASKS:
            with self.subTest(task=task["id"]):
                shown = re.findall(r"Tabulka: (\w+)", task["prompt"])
                expected = [
                    f"{table}.booked_on má typ DATE."
                    for table in shown if "booked_on" in _TABLES[table][0]
                ]
                boilerplate = task["prompt"].split("\n\n")[1]
                self.assertEqual(
                    boilerplate.replace(" NULL značí chybějící hodnotu.", ""),
                    "Použij syntaxi Oracle SQL."
                    + "".join(f" {note}" for note in expected),
                )

    def test_null_note_catalog_regressions(self):
        tasks = {task["id"]: task for task in TASKS}
        for task_id, has_note in (
            (2, False), (5, False), (14, False),
            (4, True), (9, True), (18, True), (46, True),
        ):
            with self.subTest(task=task_id):
                self.assertEqual(
                    "NULL značí chybějící hodnotu." in tasks[task_id]["prompt"], has_note,
                )

    def test_null_note_uses_only_selected_table_samples(self):
        for tables, has_note in (
            (("accounts",), False),
            (("transactions",), False),
            (("customers",), True),
            (("accounts", "customers"), True),
        ):
            with self.subTest(tables=tables):
                task = _task(
                    999, "beginner", "write-query", tables,
                    "Vypiš řádky.", "SELECT * FROM accounts;", "Použij SELECT.",
                )
                self.assertEqual("NULL značí chybějící hodnotu." in task["prompt"], has_note)

    def test_null_note_detects_semantics_in_each_text_field(self):
        defaults = {
            "instruction": "Vypiš účty.",
            "answer": "SELECT * FROM accounts;",
            "hint": "Použij SELECT.",
            "sql": None,
        }
        for field in defaults:
            for text, has_note in (
                ("balance is null", True),
                ("balance IS NOT NULL", True),
                ("nvl(balance, 0)", True),
                ("Coalesce(balance, 0)", True),
                ("NULL značí chybějící hodnotu.", True),
                ("nullable_balance, null_count, nvl_value, coalesce_value", False),
            ):
                with self.subTest(field=field, text=text):
                    task = _task(
                        999, "beginner", "find-bug", ("accounts",),
                        **{**defaults, field: text},
                    )
                    self.assertEqual(
                        "NULL značí chybějící hodnotu." in task["prompt"], has_note,
                    )

    def test_datatype_note_regressions(self):
        tasks = {task["id"]: task for task in TASKS}
        for task_id, tables, has_note in (
            (52, ["customers"], False),
            (25, ["transactions"], True),
            (21, ["accounts", "transactions"], True),
            (20, ["customers", "accounts"], False),
        ):
            with self.subTest(task=task_id):
                prompt = tasks[task_id]["prompt"]
                self.assertEqual(re.findall(r"Tabulka: (\w+)", prompt), tables)
                self.assertEqual("transactions.booked_on má typ DATE." in prompt, has_note)
                if not has_note:
                    self.assertNotIn("booked_on", prompt)

    def test_datatype_note_uses_exact_schema_columns_not_instruction(self):
        for column, has_note in (("booked_on", True), ("not_booked_on", False)):
            with self.subTest(column=column):
                with patch.dict(_TABLES, {"example": ((column,), (("NULL",),))}):
                    task = _task(
                        999, "beginner", "write-query", ("example",),
                        "Text zmiňuje booked_on.", "SELECT * FROM example;", "Nápověda.",
                    )
                self.assertEqual("example.booked_on má typ DATE." in task["prompt"], has_note)

    def test_canonical_answers_are_accepted(self):
        for task in TASKS:
            with self.subTest(task=task["id"]):
                self.assertTrue(check_answer(task["expected_answer"], task))
                self.assertFalse(check_answer("", task))
                self.assertFalse(check_answer("SELECT incorrect FROM missing_table;", task))
                if task["type"] != "explain-result":
                    normalized_variant = " \n " + task["solution"].rstrip(";") + " \n"
                    self.assertTrue(check_answer(normalized_variant, task))

    def test_find_bug_requires_corrected_sql_not_buggy_sql_or_description(self):
        for task in TASKS:
            if task["type"] == "find-bug":
                with self.subTest(task=task["id"]):
                    self.assertFalse(check_answer(task["sql"], task))
                    self.assertFalse(check_answer(task["hint"], task))

    def test_explain_result_rejects_overlapping_numeric_keywords(self):
        tasks = {task["id"]: task for task in TASKS}
        for task_id, answer in ((32, "1500"), (53, "150")):
            with self.subTest(task=task_id, answer=answer):
                self.assertFalse(check_answer(answer, tasks[task_id]))
        self.assertTrue(check_answer("Adam Novak má 1500.", tasks[32]))
        self.assertTrue(check_answer("Central má 150, South má 0.", tasks[53]))

    def test_explain_result_matches_complete_numbers_and_preserves_czech_stems(self):
        for answer in ("součet 1150", "součet -150", "součet +150",
                       "součet 150.5", "součet 150,5", "součet x150", "součet 150x"):
            with self.subTest(answer=answer):
                self.assertFalse(check_explain_result_answer(answer, ["součet", "150"]))
        for answer in ("Součet: 150.", "součet (150)", "součet 150, další údaj"):
            with self.subTest(answer=answer):
                self.assertTrue(check_explain_result_answer(answer, ["součet", "150"]))
        self.assertTrue(check_explain_result_answer(
            "Průměrný zůstatek je 1000.", ["průměr", "1000"],
        ))
        self.assertTrue(check_explain_result_answer(
            "Následující částka je -50.", ["následující", "-50"],
        ))

    def test_random_selection_supports_all_combinations_and_unknown_filters(self):
        for difficulty in ("beginner", "intermediate", "advanced"):
            for task_type in ("write-query", "find-bug", "explain-result"):
                candidates = [
                    task for task in TASKS
                    if task["difficulty"] == difficulty and task["type"] == task_type
                ]
                with patch("tasks.random.choice", return_value=candidates[-1]) as choice:
                    self.assertIs(get_random_task(difficulty, task_type), candidates[-1])
                    choice.assert_called_once_with(candidates)
        self.assertIsNone(get_random_task("unknown", "write-query"))
        self.assertIsNone(get_random_task("beginner", "unknown"))

    def test_query_results_match_sample_data(self):
        # SQLite exercises the shared SQL subset; these callbacks emulate only
        # the Oracle scalar functions used here, not the full Oracle dialect.
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.create_function("NVL", 2, lambda value, fallback: fallback if value is None else value)
        connection.create_function(
            "REGEXP_SUBSTR", 2,
            lambda value, pattern: (
                match.group(0) if value is not None and (match := re.search(pattern, value)) else None
            ),
        )
        connection.create_function(
            "REGEXP_LIKE", 2,
            lambda value, pattern: value is not None and re.search(pattern, value) is not None,
        )
        for table, (columns, rows) in _TABLES.items():
            connection.execute(f"CREATE TABLE {table} ({', '.join(columns)})")
            connection.executemany(
                f"INSERT INTO {table} VALUES ({', '.join('?' for _ in columns)})",
                [tuple(None if value == "NULL" else value for value in row) for row in rows],
            )

        expected = {
            1: [("Adam Novak",)],
            2: [(10, 1, 1, 1500, "ACTIVE"), (20, 2, 2, 500, "BLOCKED")],
            3: [("ACTIVE", 1), ("BLOCKED", 1)],
            4: [("Adam Novak", "Prague"), ("Eva Mala", "Brno")],
            5: [(10, 1500)],
            6: [(10, 1500), (20, 500)],
            7: [(10,), (20,)],
            8: [("Adam Novak",), ("Eva Mala",)],
            9: [("Adam Novak",)],
            10: [("Eva Mala",)],
            11: [(10,), (20,)],
            12: [(2,)],
            13: [(2000,)],
            14: [(1000,)],
            15: [(1,)],
            16: [("Prague",), ("Brno",)],
            17: [(2000,)],
            18: [("Eva Mala",)],
            19: [(10,)],
            20: [("Adam Novak", 1500), ("Eva Mala", 500)],
            21: [(10, 2), (20, 0)],
            22: [(1, 1500)],
            23: [(10, "HIGH"), (20, "LOW")],
            24: [(10, 1), (20, 1)],
            25: [(100, 200), (101, 150)],
            26: [("Adam Novak", 10), ("Eva Mala", 20)],
            27: [(1, 1500)],
            28: [("ACTIVE", 1500), ("BLOCKED", 500)],
            29: [(10, "POSITIVE"), (20, "POSITIVE")],
            30: [(10, 200), (20, None)],
            31: [(10,)],
            32: [("Adam Novak", 1500), ("Eva Mala", 500)],
            33: [(10, 2), (20, 0)],
            34: [(1, 1500)],
            35: [(10, 1), (20, 2)],
            36: [(100, 200), (101, 150)],
            37: [("Eva Mala",)],
            38: [(10,), (20,)],
            39: [("Adam Novak", "Central", 1500)],
            40: [(100, None), (101, 200)],
            41: [(10, 1), (20, 2)],
            42: [(1, None), (2, "example.test")],
            43: [("Eva Mala",)],
            44: [(100, None), (101, 200)],
            45: [(100, 200), (101, 150)],
            46: [(10, 150), (20, 0)],
            47: [("Eva Mala",)],
            48: [(10,)],
            49: [("Eva Mala",)],
            50: [(100, -50), (101, None)],
            51: [(20,)],
            52: [(1, "Novak"), (2, "Mala")],
            53: [("Central", 150), ("South", 0)],
            54: [(100, 150), (101, 150)],
        }
        self.assertEqual(set(expected), {task["id"] for task in TASKS})
        for task in TASKS:
            with self.subTest(task=task["id"]):
                sql = task["sql"] if task["type"] == "explain-result" else task["solution"]
                self.assertCountEqual(connection.execute(sql).fetchall(), expected[task["id"]])


if __name__ == "__main__":
    unittest.main()
