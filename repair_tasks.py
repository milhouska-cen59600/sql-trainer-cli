import ast
import pprint
import re
from pathlib import Path


def main():
    path = Path(__file__).resolve().with_name("tasks.py")
    source = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(source)

    catalog = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(
                isinstance(target, ast.Name) and target.id == "TASKS"
                for target in node.targets
            ):
                catalog = ast.literal_eval(node.value)
                break

    if not isinstance(catalog, list) or len(catalog) != 27:
        raise SystemExit(
            "Expected the Oracle catalog with 27 tasks. No changes made."
        )

    keyword_fixes = {
        7: ["klient", "p\u0159\u00edjm", "vy\u0161\u0161\u00edm", "30000"],
        8: ["transakce", "\u010d\u00e1stk", "vy\u0161\u0161\u00ed", "10000"],
        9: [
            "\u010d\u00edsla \u00fa\u010dt\u016f",
            "z\u016fstat",
            "z\u00e1porn",
        ],
        16: ["klient", "\u010d\u00edsla", "\u00fa\u010dt\u016f"],
        17: [
            "transakce",
            "sou\u010det",
            "\u00fa\u010dtu",
            "ka\u017ed\u00e9",
        ],
        18: [
            "o\u010d\u00edsluje",
            "\u00fa\u010dtu",
            "nejnov\u011bj\u0161\u00ed",
        ],
        25: ["transakce", "p\u0159edchoz\u00ed", "\u00fa\u010dtu"],
        26: ["pozn\u00e1m", "vs:", "\u0161esti", "\u010d\u00edslic"],
        27: [
            "klient",
            "\u010d\u00edslo \u00fa\u010dtu",
            "transakc",
            "50000",
        ],
    }

    for task in catalog:
        if task["id"] in keyword_fixes:
            task["keywords"] = keyword_fixes[task["id"]]

        task["prompt"] = re.sub(
            r"Tabulka:\s*(\w+)\(([^)]+)\)",
            r"Tabulka: \1\nSloupce: \2",
            task["prompt"],
        )

        if task["type"] == "explain-result":
            answer = task["expected_answer"].casefold()
            missing = [
                keyword
                for keyword in task["keywords"]
                if keyword.casefold() not in answer
            ]
            if missing:
                raise SystemExit(
                    f"Task {task['id']}: missing keywords "
                    f"{ascii(missing)}. No changes made."
                )

    header = "import random\nfrom copy import deepcopy\n\n\n"
    body = "TASKS = " + pprint.pformat(
        catalog,
        width=100,
        sort_dicts=False,
    )
    footer = '''


def generate_tasks():
    """Return an independent copy of the prepared Oracle catalog."""
    return deepcopy(TASKS)


def get_random_task(difficulty, task_type):
    filtered = [
        task
        for task in TASKS
        if task["difficulty"] == difficulty and task["type"] == task_type
    ]

    if not filtered:
        return None

    return random.choice(filtered)
'''

    updated = header + body + footer
    ast.parse(updated)

    backup = path.with_name("tasks.before-repair.bak")
    if not backup.exists():
        backup.write_bytes(path.read_bytes())

    path.write_text(updated, encoding="utf-8")
    print("OK: tasks.py updated; 27 Oracle tasks preserved.")


if __name__ == "__main__":
    main()