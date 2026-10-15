import random

TASKS = [
    {
        "id": 1,
        "difficulty": "beginner",
        "type": "find-bug",
        "prompt": "Find the error in this SQL query.",
        "sql": "SELECT name FROM customers WHERE city = Prague;",
        "hint": "Check how string values are written in SQL.",
        "solution": "Prague must be wrapped in single quotes: SELECT name FROM customers WHERE city = 'Prague';",
        "expected_answer": "Prague must be in single quotes.",
        "keywords": ["quote", "quotes", "single quotes", "apostrophe", "string"],
    },
    {
        "id": 2,
        "difficulty": "beginner",
        "type": "write-query",
        "prompt": "Write a query that selects all columns from the users table.",
        "sql": None,
        "hint": "Use SELECT with *.",
        "solution": "SELECT * FROM users;",
        "expected_answer": "SELECT * FROM users;",
        "keywords": [],
    },
    {
        "id": 3,
        "difficulty": "intermediate",
        "type": "explain-result",
        "prompt": "What does this query return?",
        "sql": "SELECT department, COUNT(*) FROM employees GROUP BY department;",
        "hint": "Think about grouping and counting rows.",
        "solution": "It returns one row per department with the number of employees in each department.",
        "expected_answer": "One row per department with employee counts.",
        "keywords": ["department", "count", "group", "employees"],
    },
    {
        "id": 4,
        "difficulty": "beginner",
        "type": "write-query",
        "prompt": "Write a query that selects the name column from the customers table.",
        "sql": None,
        "hint": "Select one column from one table.",
        "solution": "SELECT name FROM customers;",
        "expected_answer": "SELECT name FROM customers;",
        "keywords": [],
    },
]


def get_random_task(difficulty, task_type):
    filtered = [
        task for task in TASKS
        if task["difficulty"] == difficulty and task["type"] == task_type
    ]

    if not filtered:
        return None

    return random.choice(filtered)