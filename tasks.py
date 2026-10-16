import random
from copy import deepcopy


TASKS = [
    # =========================================================
    # JUNIOR
    # =========================================================
    {
        "id": 1,
        "difficulty": "beginner",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Vypiš všechny klienty, jejichž monthly_income je vyšší než 20000.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name  | city   | monthly_income\n"
            "----------+------------+------------+--------+---------------\n"
            "101       | Jan        | Novak      | Praha  | 28000\n"
            "102       | Petra      | Svobodova  | Brno   | 19000"
        ),
        "sql": None,
        "hint": "Použij WHERE monthly_income > 20000.",
        "solution": "SELECT * FROM clients WHERE monthly_income > 20000;",
        "expected_answer": "SELECT * FROM clients WHERE monthly_income > 20000;",
        "keywords": [],
    },
    {
        "id": 2,
        "difficulty": "beginner",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Získej account_number a balance pro všechny účty, kde je balance vyšší než 100000.\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000"
        ),
        "sql": None,
        "hint": "Vyber pouze account_number a balance.",
        "solution": "SELECT account_number, balance FROM accounts WHERE balance > 100000;",
        "expected_answer": "SELECT account_number, balance FROM accounts WHERE balance > 100000;",
        "keywords": [],
    },
    {
        "id": 3,
        "difficulty": "beginner",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Vypiš všechny transakce typu 'WITHDRAWAL'.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type | note\n"
            "---------------+------------+------------------+--------+------------------+-----------\n"
            "9001           | 5001       | 2024-01-10       | 1500   | WITHDRAWAL       | ATM Praha\n"
            "9002           | 5002       | 2024-01-12       | 8000   | DEPOSIT          | Cash desk"
        ),
        "sql": None,
        "hint": "Použij WHERE transaction_type = 'WITHDRAWAL'.",
        "solution": "SELECT * FROM transactions WHERE transaction_type = 'WITHDRAWAL';",
        "expected_answer": "SELECT * FROM transactions WHERE transaction_type = 'WITHDRAWAL';",
        "keywords": [],
    },
    {
        "id": 4,
        "difficulty": "beginner",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vypsat first_name klientů z města Praha, ale obsahuje chybu.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name  | city\n"
            "----------+------------+------------+-------\n"
            "101       | Jan        | Novak      | Praha\n"
            "102       | Petra      | Svobodova  | Brno\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": "SELECT first_name FROM clients WHERE city = Praha;",
        "hint": "Textová hodnota musí být v jednoduchých uvozovkách.",
        "solution": "SELECT first_name FROM clients WHERE city = 'Praha';",
        "expected_answer": "SELECT first_name FROM clients WHERE city = 'Praha';",
        "keywords": [],
    },
    {
        "id": 5,
        "difficulty": "beginner",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit čísla účtů s balance vyšší než 50000, ale je v něm překlep.\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": "SELECT account_number FORM accounts WHERE balance > 50000;",
        "hint": "Zkontroluj správný zápis FROM.",
        "solution": "SELECT account_number FROM accounts WHERE balance > 50000;",
        "expected_answer": "SELECT account_number FROM accounts WHERE balance > 50000;",
        "keywords": [],
    },
    {
        "id": 6,
        "difficulty": "beginner",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit všechny úvěry s interest_rate vyšší než 5, ale používá chybný název sloupce.\n\n"
            "Tabulka: loans\n"
            "loan_id | client_id | loan_amount | interest_rate | status\n"
            "--------+-----------+-------------+---------------+--------\n"
            "3001    | 101       | 250000      | 4.9           | ACTIVE\n"
            "3002    | 102       | 180000      | 6.1           | ACTIVE\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": "SELECT * FROM loans WHERE interest > 5;",
        "hint": "Použij přesný název sloupce.",
        "solution": "SELECT * FROM loans WHERE interest_rate > 5;",
        "expected_answer": "SELECT * FROM loans WHERE interest_rate > 5;",
        "keywords": [],
    },
    {
        "id": 7,
        "difficulty": "beginner",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name  | city   | monthly_income\n"
            "----------+------------+------------+--------+---------------\n"
            "101       | Jan        | Novak      | Praha  | 28000\n"
            "102       | Petra      | Svobodova  | Brno   | 42000"
        ),
        "sql": "SELECT * FROM clients WHERE monthly_income > 30000;",
        "hint": "Zaměř se na filtr a na to, že SELECT * vrací všechny sloupce.",
        "solution": (
            "Dotaz vrátí všechny sloupce všech klientů, jejichž monthly_income je vyšší než 30000."
        ),
        "expected_answer": (
            "Dotaz vrátí všechny klienty s monthly_income vyšším než 30000."
        ),
        "keywords": ["klient", "monthly_income", "vyšším", "30000"],
    },
    {
        "id": 8,
        "difficulty": "beginner",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type | note\n"
            "---------------+------------+------------------+--------+------------------+-----------\n"
            "9001           | 5001       | 2024-01-10       | 1500   | WITHDRAWAL       | ATM Praha\n"
            "9002           | 5002       | 2024-01-12       | 12000  | DEPOSIT          | Cash desk"
        ),
        "sql": "SELECT * FROM transactions WHERE amount > 10000;",
        "hint": "Zaměř se na amount > 10000.",
        "solution": (
            "Dotaz vrátí všechny transakce, jejichž amount je vyšší než 10000."
        ),
        "expected_answer": (
            "Dotaz vrátí transakce s amount vyšším než 10000."
        ),
        "keywords": ["transakce", "amount", "vyšším", "10000"],
    },
    {
        "id": 9,
        "difficulty": "beginner",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | -200\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000"
        ),
        "sql": "SELECT account_number, balance FROM accounts WHERE balance < 0;",
        "hint": "Vrací jen dva sloupce a pouze záporný balance.",
        "solution": (
            "Dotaz vrátí account_number a balance pro účty se záporným zůstatkem."
        ),
        "expected_answer": (
            "Dotaz vrátí account_number a balance účtů se záporným balance."
        ),
        "keywords": ["account_number", "balance", "záporn"],
    },

    # =========================================================
    # INTERMEDIATE
    # =========================================================
    {
        "id": 10,
        "difficulty": "intermediate",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Vypiš jméno klienta a číslo jeho účtu.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "102       | Petra      | Svobodova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000\n\n"
            "Vazba:\n"
            "accounts.client_id = clients.client_id"
        ),
        "sql": None,
        "hint": "Použij JOIN mezi clients a accounts.",
        "solution": (
            "SELECT c.first_name, c.last_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "expected_answer": (
            "SELECT c.first_name, c.last_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "keywords": [],
    },
    {
        "id": 11,
        "difficulty": "intermediate",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Očísluj transakce každého účtu od nejnovější po nejstarší pomocí ROW_NUMBER().\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type\n"
            "---------------+------------+------------------+--------+-----------------\n"
            "9001           | 5001       | 2024-01-10       | 1500   | WITHDRAWAL\n"
            "9002           | 5001       | 2024-01-12       | 8000   | DEPOSIT"
        ),
        "sql": None,
        "hint": "Použij PARTITION BY account_id ORDER BY transaction_date DESC.",
        "solution": (
            "SELECT account_id, transaction_date, amount, "
            "ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY transaction_date DESC) AS row_num "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT account_id, transaction_date, amount, "
            "ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY transaction_date DESC) AS row_num "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 12,
        "difficulty": "intermediate",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "U každé transakce zobraz také celkový součet amount na stejném účtu.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type\n"
            "---------------+------------+------------------+--------+-----------------\n"
            "9001           | 5001       | 2024-01-10       | 1500   | WITHDRAWAL\n"
            "9002           | 5001       | 2024-01-12       | 8000   | DEPOSIT"
        ),
        "sql": None,
        "hint": "Použij SUM(amount) OVER (PARTITION BY account_id).",
        "solution": (
            "SELECT transaction_id, account_id, amount, "
            "SUM(amount) OVER (PARTITION BY account_id) AS total_amount_per_account "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT transaction_id, account_id, amount, "
            "SUM(amount) OVER (PARTITION BY account_id) AS total_amount_per_account "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 13,
        "difficulty": "intermediate",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Vypiš všechny klienty a případně čísla jejich účtů, tedy i klienty bez účtu.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "103       | Eva        | Dvorakova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000"
        ),
        "sql": None,
        "hint": "Použij LEFT JOIN.",
        "solution": (
            "SELECT c.first_name, c.last_name, a.account_number "
            "FROM clients c LEFT JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "expected_answer": (
            "SELECT c.first_name, c.last_name, a.account_number "
            "FROM clients c LEFT JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "keywords": [],
    },
    {
        "id": 14,
        "difficulty": "intermediate",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Zjisti počet účtů každého klienta, ale zobraz jen klienty s více než jedním účtem.\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5003       | 101       | CZ5508000000199999999999   | 30000"
        ),
        "sql": None,
        "hint": "Použij GROUP BY client_id a HAVING COUNT(*) > 1.",
        "solution": (
            "SELECT client_id, COUNT(*) "
            "FROM accounts "
            "GROUP BY client_id "
            "HAVING COUNT(*) > 1;"
        ),
        "expected_answer": (
            "SELECT client_id, COUNT(*) "
            "FROM accounts "
            "GROUP BY client_id "
            "HAVING COUNT(*) > 1;"
        ),
        "keywords": [],
    },
    {
        "id": 15,
        "difficulty": "intermediate",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "U každé transakce zobraz text, zda jde o vysokou nebo běžnou amount.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type\n"
            "---------------+------------+------------------+--------+-----------------\n"
            "9001           | 5001       | 2024-01-10       | 1500   | WITHDRAWAL\n"
            "9003           | 5001       | 2024-01-20       | 78000  | TRANSFER"
        ),
        "sql": None,
        "hint": "Použij CASE WHEN amount > 50000 THEN 'HIGH' ELSE 'STANDARD' END.",
        "solution": (
            "SELECT transaction_id, amount, "
            "CASE WHEN amount > 50000 THEN 'HIGH' ELSE 'STANDARD' END AS transaction_level "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT transaction_id, amount, "
            "CASE WHEN amount > 50000 THEN 'HIGH' ELSE 'STANDARD' END AS transaction_level "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 16,
        "difficulty": "intermediate",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit jméno klienta a číslo účtu, ale obsahuje chybu v JOIN.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "102       | Petra      | Svobodova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.account_id;"
        ),
        "hint": "Účet se váže přes client_id, ne account_id.",
        "solution": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "expected_answer": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "keywords": [],
    },
    {
        "id": 17,
        "difficulty": "intermediate",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má spočítat počet účtů každého klienta, ale chybí správná klauzule.\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5003       | 101       | CZ5508000000199999999999   | 30000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": "SELECT client_id, COUNT(*) FROM accounts;",
        "hint": "Pokud používáš COUNT(*) s client_id, musíš seskupovat.",
        "solution": "SELECT client_id, COUNT(*) FROM accounts GROUP BY client_id;",
        "expected_answer": "SELECT client_id, COUNT(*) FROM accounts GROUP BY client_id;",
        "keywords": [],
    },
    {
        "id": 18,
        "difficulty": "intermediate",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má očíslovat transakce v rámci účtu, ale analytická funkce je neúplná.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9002           | 5001       | 2024-01-12       | 8000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT account_id, transaction_date, "
            "ROW_NUMBER() OVER (ORDER BY transaction_date DESC) AS row_num "
            "FROM transactions;"
        ),
        "hint": "Pořadí se má počítat zvlášť pro každý účet.",
        "solution": (
            "SELECT account_id, transaction_date, "
            "ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY transaction_date DESC) AS row_num "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT account_id, transaction_date, "
            "ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY transaction_date DESC) AS row_num "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 19,
        "difficulty": "intermediate",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit všechny klienty i bez účtu, ale je v něm chyba v typu JOIN.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "103       | Eva        | Dvorakova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "hint": "Pokud chceš i klienty bez účtu, nestačí JOIN.",
        "solution": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c LEFT JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "expected_answer": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c LEFT JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "keywords": [],
    },
    {
        "id": 20,
        "difficulty": "intermediate",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit jen klienty s více než jedním účtem, ale agregaci filtruje špatně.\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5003       | 101       | CZ5508000000199999999999\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT client_id, COUNT(*) "
            "FROM accounts "
            "WHERE COUNT(*) > 1 "
            "GROUP BY client_id;"
        ),
        "hint": "Agregaci filtruj pomocí HAVING.",
        "solution": (
            "SELECT client_id, COUNT(*) "
            "FROM accounts "
            "GROUP BY client_id "
            "HAVING COUNT(*) > 1;"
        ),
        "expected_answer": (
            "SELECT client_id, COUNT(*) "
            "FROM accounts "
            "GROUP BY client_id "
            "HAVING COUNT(*) > 1;"
        ),
        "keywords": [],
    },
    {
        "id": 21,
        "difficulty": "intermediate",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má označit vysoké transakce pomocí CASE, ale má chybnou podmínku.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | amount\n"
            "---------------+-------\n"
            "9001           | 1500\n"
            "9003           | 78000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT transaction_id, amount, "
            "CASE WHEN amount < 50000 THEN 'HIGH' ELSE 'STANDARD' END AS transaction_level "
            "FROM transactions;"
        ),
        "hint": "HIGH má být pro vyšší amount.",
        "solution": (
            "SELECT transaction_id, amount, "
            "CASE WHEN amount > 50000 THEN 'HIGH' ELSE 'STANDARD' END AS transaction_level "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT transaction_id, amount, "
            "CASE WHEN amount > 50000 THEN 'HIGH' ELSE 'STANDARD' END AS transaction_level "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 22,
        "difficulty": "intermediate",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "102       | Petra      | Svobodova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number              | balance\n"
            "-----------+-----------+-----------------------------+--------\n"
            "5001       | 101       | CZ6508000000192000145399   | 125000\n"
            "5002       | 102       | CZ1201000000198765432107   | 54000\n\n"
            "Vazba:\n"
            "accounts.client_id = clients.client_id"
        ),
        "sql": (
            "SELECT c.first_name, c.last_name, a.account_number "
            "FROM clients c JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "hint": "JOIN propojí klienty s jejich účty.",
        "solution": (
            "Dotaz vrátí first_name, last_name a account_number klientů."
        ),
        "expected_answer": (
            "Dotaz vrátí klienty a jejich account_number."
        ),
        "keywords": ["klient", "account_number"],
    },
    {
        "id": 23,
        "difficulty": "intermediate",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9002           | 5001       | 2024-01-12       | 8000"
        ),
        "sql": (
            "SELECT account_id, amount, "
            "SUM(amount) OVER (PARTITION BY account_id) AS total_amount_per_account "
            "FROM transactions;"
        ),
        "hint": "Analytická SUM neslučuje řádky, jen doplní vypočtenou hodnotu.",
        "solution": (
            "Dotaz vrátí transakce a u každé zobrazí total_amount_per_account pro stejný účet."
        ),
        "expected_answer": (
            "Dotaz vrátí transakce a u každé zobrazí total_amount_per_account stejného účtu."
        ),
        "keywords": ["transakce", "total_amount_per_account", "každé"],
    },
    {
        "id": 24,
        "difficulty": "intermediate",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9002           | 5001       | 2024-01-12       | 8000"
        ),
        "sql": (
            "SELECT account_id, transaction_date, "
            "ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY transaction_date DESC) AS row_num "
            "FROM transactions;"
        ),
        "hint": "ROW_NUMBER čísluje řádky v rámci account_id.",
        "solution": (
            "Dotaz očísluje transakce v rámci každého account_id od nejnovější po nejstarší."
        ),
        "expected_answer": (
            "Dotaz očísluje transakce v rámci každého account_id od nejnovější po nejstarší."
        ),
        "keywords": ["očísluje", "transakce", "account_id"],
    },
    {
        "id": 25,
        "difficulty": "intermediate",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "103       | Eva        | Dvorakova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107"
        ),
        "sql": (
            "SELECT c.first_name, a.account_number "
            "FROM clients c LEFT JOIN accounts a ON c.client_id = a.client_id;"
        ),
        "hint": "LEFT JOIN zachová všechny klienty.",
        "solution": (
            "Dotaz vrátí všechny klienty a pokud mají účet, tak i account_number."
        ),
        "expected_answer": (
            "Dotaz vrátí všechny klienty a případně jejich account_number."
        ),
        "keywords": ["všechny klienty", "account_number"],
    },

    # =========================================================
    # ADVANCED
    # =========================================================
    {
        "id": 26,
        "difficulty": "advanced",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Vypiš first_name klienta, account_number a amount pro všechny transakce vyšší než 50000.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "102       | Petra      | Svobodova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type\n"
            "---------------+------------+------------------+--------+-----------------\n"
            "9001           | 5001       | 2024-01-10       | 1500   | WITHDRAWAL\n"
            "9003           | 5001       | 2024-01-20       | 78000  | TRANSFER\n\n"
            "Vazby:\n"
            "accounts.client_id = clients.client_id\n"
            "transactions.account_id = accounts.account_id"
        ),
        "sql": None,
        "hint": "Budeš potřebovat spojit 3 tabulky.",
        "solution": (
            "SELECT c.first_name, a.account_number, t.amount "
            "FROM clients c "
            "JOIN accounts a ON c.client_id = a.client_id "
            "JOIN transactions t ON a.account_id = t.account_id "
            "WHERE t.amount > 50000;"
        ),
        "expected_answer": (
            "SELECT c.first_name, a.account_number, t.amount "
            "FROM clients c "
            "JOIN accounts a ON c.client_id = a.client_id "
            "JOIN transactions t ON a.account_id = t.account_id "
            "WHERE t.amount > 50000;"
        ),
        "keywords": [],
    },
    {
        "id": 27,
        "difficulty": "advanced",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "U každé transakce zobraz také amount předchozí transakce na stejném účtu podle data.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9002           | 5001       | 2024-01-12       | 8000"
        ),
        "sql": None,
        "hint": "Použij LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date).",
        "solution": (
            "SELECT account_id, transaction_date, amount, "
            "LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS previous_amount "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT account_id, transaction_date, amount, "
            "LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS previous_amount "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 28,
        "difficulty": "advanced",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Najdi všechny transakce, jejichž note začíná VS: a pokračuje přesně šesti číslicemi.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | transaction_type | note\n"
            "---------------+------------+------------------+--------+------------------+-----------\n"
            "9005           | 5001       | 2024-02-01       | 12000  | TRANSFER         | VS:123456\n"
            "9006           | 5001       | 2024-02-02       | 5000   | TRANSFER         | VS:12345A"
        ),
        "sql": None,
        "hint": "Použij REGEXP_LIKE(note, '^VS:[0-9]{6}$').",
        "solution": (
            "SELECT * FROM transactions "
            "WHERE REGEXP_LIKE(note, '^VS:[0-9]{6}$');"
        ),
        "expected_answer": (
            "SELECT * FROM transactions "
            "WHERE REGEXP_LIKE(note, '^VS:[0-9]{6}$');"
        ),
        "keywords": [],
    },
    {
        "id": 29,
        "difficulty": "advanced",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Z note transakce vytáhni šestimístný variabilní symbol ve formátu VS:123456.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | note\n"
            "---------------+----------------\n"
            "9005           | VS:123456\n"
            "9006           | salary payment"
        ),
        "sql": None,
        "hint": "Použij REGEXP_SUBSTR(note, 'VS:[0-9]{6}').",
        "solution": (
            "SELECT transaction_id, REGEXP_SUBSTR(note, 'VS:[0-9]{6}') AS variable_symbol "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT transaction_id, REGEXP_SUBSTR(note, 'VS:[0-9]{6}') AS variable_symbol "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 30,
        "difficulty": "advanced",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Vrať klienty, kteří nemají žádný účet.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "103       | Eva        | Dvorakova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107"
        ),
        "sql": None,
        "hint": "Použij NOT EXISTS.",
        "solution": (
            "SELECT c.client_id, c.first_name, c.last_name "
            "FROM clients c "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.client_id = c.client_id);"
        ),
        "expected_answer": (
            "SELECT c.client_id, c.first_name, c.last_name "
            "FROM clients c "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.client_id = c.client_id);"
        ),
        "keywords": [],
    },
    {
        "id": 31,
        "difficulty": "advanced",
        "type": "write-query",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Seřaď transakce podle amount v rámci každého účtu a přiřaď pořadí pomocí RANK().\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | amount\n"
            "---------------+------------+-------\n"
            "9001           | 5001       | 1500\n"
            "9003           | 5001       | 78000"
        ),
        "sql": None,
        "hint": "Použij RANK() OVER (PARTITION BY account_id ORDER BY amount DESC).",
        "solution": (
            "SELECT account_id, amount, "
            "RANK() OVER (PARTITION BY account_id ORDER BY amount DESC) AS amount_rank "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT account_id, amount, "
            "RANK() OVER (PARTITION BY account_id ORDER BY amount DESC) AS amount_rank "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 32,
        "difficulty": "advanced",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit first_name klienta a amount transakce nad 50000, ale obsahuje chybu v JOIN.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "102       | Petra      | Svobodova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9003           | 5001       | 2024-01-20       | 78000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT c.first_name, t.amount "
            "FROM clients c "
            "JOIN accounts a ON c.client_id = a.client_id "
            "JOIN transactions t ON c.client_id = t.account_id "
            "WHERE t.amount > 50000;"
        ),
        "hint": "Transactions se vážou na accounts přes account_id.",
        "solution": (
            "SELECT c.first_name, t.amount "
            "FROM clients c "
            "JOIN accounts a ON c.client_id = a.client_id "
            "JOIN transactions t ON a.account_id = t.account_id "
            "WHERE t.amount > 50000;"
        ),
        "expected_answer": (
            "SELECT c.first_name, t.amount "
            "FROM clients c "
            "JOIN accounts a ON c.client_id = a.client_id "
            "JOIN transactions t ON a.account_id = t.account_id "
            "WHERE t.amount > 50000;"
        ),
        "keywords": [],
    },
    {
        "id": 33,
        "difficulty": "advanced",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit previous_amount transakce na stejném účtu, ale chybí PARTITION BY.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9002           | 5001       | 2024-01-12       | 8000\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT account_id, transaction_date, amount, "
            "LAG(amount) OVER (ORDER BY transaction_date) AS previous_amount "
            "FROM transactions;"
        ),
        "hint": "Předchozí transakce má být v rámci stejného účtu.",
        "solution": (
            "SELECT account_id, transaction_date, amount, "
            "LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS previous_amount "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT account_id, transaction_date, amount, "
            "LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS previous_amount "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 34,
        "difficulty": "advanced",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má najít note ve formátu VS: a šesti číslic, ale regexp hledá jen pět číslic.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | note\n"
            "---------------+------------+-----------\n"
            "9005           | 5001       | VS:123456\n"
            "9006           | 5001       | VS:12345A\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT * FROM transactions "
            "WHERE REGEXP_LIKE(note, '^VS:[0-9]{5}$');"
        ),
        "hint": "Po VS: má být přesně šest číslic.",
        "solution": (
            "SELECT * FROM transactions "
            "WHERE REGEXP_LIKE(note, '^VS:[0-9]{6}$');"
        ),
        "expected_answer": (
            "SELECT * FROM transactions "
            "WHERE REGEXP_LIKE(note, '^VS:[0-9]{6}$');"
        ),
        "keywords": [],
    },
    {
        "id": 35,
        "difficulty": "advanced",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vrátit klienty bez účtu pomocí NOT EXISTS, ale poddotaz používá chybnou vazbu.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "103       | Eva        | Dvorakova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT c.client_id, c.first_name, c.last_name "
            "FROM clients c "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.account_id = c.client_id);"
        ),
        "hint": "Porovnávej client_id s client_id.",
        "solution": (
            "SELECT c.client_id, c.first_name, c.last_name "
            "FROM clients c "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.client_id = c.client_id);"
        ),
        "expected_answer": (
            "SELECT c.client_id, c.first_name, c.last_name "
            "FROM clients c "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.client_id = c.client_id);"
        ),
        "keywords": [],
    },
    {
        "id": 36,
        "difficulty": "advanced",
        "type": "find-bug",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Úkol:\n"
            "Dotaz má vytáhnout variable_symbol z note, ale používá špatnou regexp funkci.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | note\n"
            "---------------+----------------\n"
            "9005           | VS:123456\n"
            "9006           | salary payment\n\n"
            "Oprav SQL dotaz přímo v editoru."
        ),
        "sql": (
            "SELECT transaction_id, REGEXP_LIKE(note, 'VS:[0-9]{6}') AS variable_symbol "
            "FROM transactions;"
        ),
        "hint": "REGEXP_LIKE vrací podmínku, ne textový výřez.",
        "solution": (
            "SELECT transaction_id, REGEXP_SUBSTR(note, 'VS:[0-9]{6}') AS variable_symbol "
            "FROM transactions;"
        ),
        "expected_answer": (
            "SELECT transaction_id, REGEXP_SUBSTR(note, 'VS:[0-9]{6}') AS variable_symbol "
            "FROM transactions;"
        ),
        "keywords": [],
    },
    {
        "id": 37,
        "difficulty": "advanced",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount\n"
            "---------------+------------+------------------+-------\n"
            "9001           | 5001       | 2024-01-10       | 1500\n"
            "9002           | 5001       | 2024-01-12       | 8000"
        ),
        "sql": (
            "SELECT account_id, transaction_date, amount, "
            "LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_date) AS previous_amount "
            "FROM transactions;"
        ),
        "hint": "LAG vrací hodnotu z předchozího řádku ve stejné skupině.",
        "solution": (
            "Dotaz vrátí transakce a u každé zobrazí previous_amount předchozí transakce stejného účtu."
        ),
        "expected_answer": (
            "Dotaz vrátí transakce a u každé zobrazí previous_amount předchozí transakce stejného účtu."
        ),
        "keywords": ["transakce", "previous_amount", "předchozí"],
    },
    {
        "id": 38,
        "difficulty": "advanced",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | transaction_date | amount | note\n"
            "---------------+------------+------------------+--------+-----------\n"
            "9005           | 5001       | 2024-02-01       | 12000  | VS:123456\n"
            "9006           | 5001       | 2024-02-02       | 5000   | VS:12345A"
        ),
        "sql": (
            "SELECT * FROM transactions "
            "WHERE REGEXP_LIKE(note, '^VS:[0-9]{6}$');"
        ),
        "hint": "Zaměř se na vzor v note.",
        "solution": (
            "Dotaz vrátí transakce, jejichž note přesně odpovídá formátu VS: následovanému šesti číslicemi."
        ),
        "expected_answer": (
            "Dotaz vrátí transakce s note ve formátu VS: a šesti číslicemi."
        ),
        "keywords": ["transakce", "note", "VS", "šesti"],
    },
    {
        "id": 39,
        "difficulty": "advanced",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name\n"
            "----------+-----------\n"
            "101       | Jan\n"
            "102       | Petra\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | amount\n"
            "---------------+------------+-------\n"
            "9001           | 5001       | 1500\n"
            "9003           | 5001       | 78000"
        ),
        "sql": (
            "SELECT c.first_name, a.account_number, t.amount "
            "FROM clients c "
            "JOIN accounts a ON c.client_id = a.client_id "
            "JOIN transactions t ON a.account_id = t.account_id "
            "WHERE t.amount > 50000;"
        ),
        "hint": "Zaměř se na spojení 3 tabulek a filtr podle amount.",
        "solution": (
            "Dotaz vrátí first_name klienta, account_number a amount transakcí vyšších než 50000."
        ),
        "expected_answer": (
            "Dotaz vrátí klienta, account_number a amount transakcí vyšších než 50000."
        ),
        "keywords": ["klient", "account_number", "amount", "50000"],
    },
    {
        "id": 40,
        "difficulty": "advanced",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: clients\n"
            "client_id | first_name | last_name\n"
            "----------+------------+-----------\n"
            "101       | Jan        | Novak\n"
            "103       | Eva        | Dvorakova\n\n"
            "Tabulka: accounts\n"
            "account_id | client_id | account_number\n"
            "-----------+-----------+-----------------------------\n"
            "5001       | 101       | CZ6508000000192000145399\n"
            "5002       | 102       | CZ1201000000198765432107"
        ),
        "sql": (
            "SELECT c.client_id, c.first_name, c.last_name "
            "FROM clients c "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.client_id = c.client_id);"
        ),
        "hint": "NOT EXISTS vrací klienty, ke kterým neexistuje účet.",
        "solution": (
            "Dotaz vrátí klienty, kteří nemají žádný účet."
        ),
        "expected_answer": (
            "Dotaz vrátí klienty bez účtu."
        ),
        "keywords": ["klienty", "bez účtu"],
    },
    {
        "id": 41,
        "difficulty": "advanced",
        "type": "explain-result",
        "prompt": (
            "Pracuješ v Oracle databázi.\n\n"
            "Vysvětli, co vrátí následující SQL dotaz.\n\n"
            "Tabulka: transactions\n"
            "transaction_id | account_id | amount\n"
            "---------------+------------+-------\n"
            "9001           | 5001       | 1500\n"
            "9003           | 5001       | 78000"
        ),
        "sql": (
            "SELECT account_id, amount, "
            "RANK() OVER (PARTITION BY account_id ORDER BY amount DESC) AS amount_rank "
            "FROM transactions;"
        ),
        "hint": "RANK určuje pořadí amount v rámci stejného účtu.",
        "solution": (
            "Dotaz vrátí transakce a pořadí jejich amount v rámci stejného account_id od nejvyšší."
        ),
        "expected_answer": (
            "Dotaz vrátí transakce a pořadí amount v rámci account_id od nejvyšší."
        ),
        "keywords": ["transakce", "pořadí", "amount", "account_id"],
    },
]


def generate_tasks():
    """Vrátí nezávislou kopii připravené sady úloh."""
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