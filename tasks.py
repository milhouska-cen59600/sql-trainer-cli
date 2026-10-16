import random


_TABLES = {
    "customers": (
        ("customer_id", "name", "city", "email"),
        ((1, "Adam Novak", "Prague", "NULL"), (2, "Eva Mala", "Brno", "eva@example.test")),
    ),
    "accounts": (
        ("account_id", "customer_id", "branch_id", "balance", "status"),
        ((10, 1, 1, 1500, "ACTIVE"), (20, 2, 2, 500, "BLOCKED")),
    ),
    "transactions": (
        ("transaction_id", "account_id", "amount", "booked_on", "kind"),
        ((100, 10, 200, "2026-01-10", "CREDIT"), (101, 10, -50, "2026-01-10", "DEBIT")),
    ),
    "branches": (
        ("branch_id", "name", "city"),
        ((1, "Central", "Prague"), (2, "South", "Brno")),
    ),
    "loans": (
        ("loan_id", "customer_id", "principal", "status"),
        ((1000, 1, 10000, "APPROVED"), (1001, 2, 5000, "PENDING")),
    ),
}


def _task(task_id, difficulty, task_type, tables, instruction, answer, hint,
          sql=None, keywords=()):
    sections = [
        "Úkol: " + instruction,
        "Použij syntaxi Oracle SQL. NULL značí chybějící hodnotu; booked_on má typ DATE.",
    ]
    for name in tables:
        columns, rows = _TABLES[name]
        cells = [columns] + [tuple(str(value) for value in row) for row in rows]
        widths = [max(len(row[index]) for row in cells) for index in range(len(columns))]
        border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
        lines = [
            "| " + " | ".join(value.ljust(width) for value, width in zip(row, widths)) + " |"
            for row in cells
        ]
        sections.append(
            f"Tabulka: {name}\n{border}\n{lines[0]}\n{border}\n"
            + "\n".join(lines[1:]) + f"\n{border}"
        )
    if task_type == "find-bug":
        sections.append("Odpověz celým opraveným SQL dotazem, nikoli popisem chyby.")
    if task_type in ("write-query", "find-bug"):
        sections.append(
            "Kontrola porovnává tokeny SQL bez ohledu na velikost písmen mimo textové "
            "literály, mezery mezi tokeny a jeden koncový středník. Obsah textových "
            "literálů musí odpovídat přesně. Dodrž pořadí sloupců a uvedené aliasy; "
            "nepřidávej další aliasy ani řazení. Nápověda upřesňuje očekávaný zápis."
        )
    return {
        "id": task_id,
        "difficulty": difficulty,
        "type": task_type,
        "prompt": "\n\n".join(sections),
        "sql": sql,
        "hint": hint,
        "solution": answer,
        "expected_answer": answer,
        "keywords": list(keywords),
    }


TASKS = [
    # Beginner: šest úloh od každého typu.
    _task(
        1, "beginner", "find-bug", ("customers",),
        "Oprav zápis textové hodnoty ve filtru města.",
        "SELECT name FROM customers WHERE city = 'Prague';",
        "Textový literál musí být v jednoduchých uvozovkách.",
        sql="SELECT name FROM customers WHERE city = Prague;",
    ),
    _task(
        2, "beginner", "write-query", ("accounts",),
        "Vypiš všechny sloupce účtů.",
        "SELECT * FROM accounts;",
        "Použij SELECT * FROM accounts.",
    ),
    _task(
        4, "beginner", "write-query", ("customers",),
        "Vypiš pouze name a city zákazníků v tomto pořadí.",
        "SELECT name, city FROM customers;",
        "Za SELECT uveď name, city.",
    ),
    _task(
        5, "beginner", "write-query", ("accounts",),
        "Vypiš account_id a balance účtů se zůstatkem větším než 1000.",
        "SELECT account_id, balance FROM accounts WHERE balance > 1000;",
        "Použij WHERE balance > 1000.",
    ),
    _task(
        6, "beginner", "write-query", ("accounts",),
        "Vypiš account_id a balance, seřaď sestupně podle balance.",
        "SELECT account_id, balance FROM accounts ORDER BY balance DESC;",
        "Použij ORDER BY balance DESC.",
    ),
    _task(
        7, "beginner", "write-query", ("accounts",),
        "Vypiš account_id účtů se zůstatkem od 500 do 1500 včetně obou mezí.",
        "SELECT account_id FROM accounts WHERE balance BETWEEN 500 AND 1500;",
        "Použij BETWEEN 500 AND 1500.",
    ),
    _task(
        8, "beginner", "write-query", ("customers",),
        "Vypiš name zákazníků z měst Prague nebo Brno pomocí IN.",
        "SELECT name FROM customers WHERE city IN ('Prague', 'Brno');",
        "Použij IN ('Prague', 'Brno') v uvedeném pořadí.",
    ),
    _task(
        9, "beginner", "find-bug", ("customers",),
        "Oprav test chybějícího e-mailu.",
        "SELECT name FROM customers WHERE email IS NULL;",
        "NULL se testuje pomocí IS NULL.",
        sql="SELECT name FROM customers WHERE email = NULL;",
    ),
    _task(
        10, "beginner", "find-bug", ("customers",),
        "Oprav vzor LIKE tak, aby vybral jména začínající na Eva.",
        "SELECT name FROM customers WHERE name LIKE 'Eva%';",
        "Pro libovolný počet znaků používá SQL znak % místo *.",
        sql="SELECT name FROM customers WHERE name LIKE 'Eva*';",
    ),
    _task(
        11, "beginner", "find-bug", ("accounts",),
        "Oprav pořadí klauzulí; zachovej filtr i sestupné řazení.",
        "SELECT account_id FROM accounts WHERE balance > 0 ORDER BY balance DESC;",
        "WHERE musí předcházet ORDER BY.",
        sql="SELECT account_id FROM accounts ORDER BY balance DESC WHERE balance > 0;",
    ),
    _task(
        12, "beginner", "find-bug", ("accounts",),
        "Dotaz má spočítat všechny účty. Oprav neplatný argument COUNT.",
        "SELECT COUNT(*) FROM accounts;",
        "Pro počet všech řádků použij COUNT(*).",
        sql="SELECT COUNT() FROM accounts;",
    ),
    _task(
        13, "beginner", "find-bug", ("accounts",),
        "Oprav neexistující název sloupce pro součet zůstatků.",
        "SELECT SUM(balance) FROM accounts;",
        "Sloupec se jmenuje balance, nikoli balances.",
        sql="SELECT SUM(balances) FROM accounts;",
    ),
    _task(
        14, "beginner", "explain-result", ("accounts",),
        "Jaká je průměrná hodnota vrácená dotazem? Uveď význam i číslo.",
        "Průměrný zůstatek je 1000.",
        "Sečti 1500 a 500 a vyděl počtem účtů.",
        sql="SELECT AVG(balance) FROM accounts;",
        keywords=("průměr", "1000"),
    ),
    _task(
        15, "beginner", "explain-result", ("customers",),
        "Kolik vyplněných e-mailů dotaz spočítá? Uveď význam i počet.",
        "Počet vyplněných e-mailů je 1; NULL se nepočítá.",
        "COUNT(sloupec) ignoruje NULL.",
        sql="SELECT COUNT(email) FROM customers;",
        keywords=("počet", "1", "null"),
    ),
    _task(
        16, "beginner", "explain-result", ("customers",),
        "Která města vrátí dotaz a proč nejsou opakovaná? Pořadí není zaručeno.",
        "Vrátí unikátní města Prague a Brno.",
        "DISTINCT odstraňuje duplicity.",
        sql="SELECT DISTINCT city FROM customers;",
        keywords=("unikátní", "prague", "brno"),
    ),
    _task(
        17, "beginner", "explain-result", ("accounts",),
        "Jaký celkový zůstatek dotaz vrátí? Uveď význam i hodnotu.",
        "Celkový součet zůstatků je 2000.",
        "SUM sčítá zůstatky všech účtů.",
        sql="SELECT SUM(balance) FROM accounts;",
        keywords=("součet", "2000"),
    ),
    _task(
        18, "beginner", "explain-result", ("customers",),
        "Které jméno vrátí filtr na známý e-mail a proč?",
        "Vrátí Eva Mala, protože má vyplněný e-mail.",
        "IS NOT NULL ponechá jen vyplněné hodnoty.",
        sql="SELECT name FROM customers WHERE email IS NOT NULL;",
        keywords=("eva mala", "vyplněný"),
    ),
    _task(
        19, "beginner", "explain-result", ("accounts",),
        "Které account_id vrátí kombinace podmínek a jaký stav má tento účet?",
        "Vrátí účet 10, který má stav ACTIVE a kladný zůstatek.",
        "Obě podmínky spojené AND musí platit současně.",
        sql="SELECT account_id FROM accounts WHERE status = 'ACTIVE' AND balance > 0;",
        keywords=("10", "active", "kladný"),
    ),
    # Intermediate: joiny, agregace a základy analytických funkcí.
    _task(
        3, "intermediate", "explain-result", ("accounts",),
        "Popiš seskupení i počty účtů v jednotlivých stavech.",
        "Pro každý stav vrátí počet účtů: ACTIVE má 1 a BLOCKED má 1.",
        "GROUP BY vytvoří jednu skupinu pro každý stav.",
        sql="SELECT status, COUNT(*) FROM accounts GROUP BY status;",
        keywords=("stav", "počet", "active", "blocked"),
    ),
    _task(
        20, "intermediate", "write-query", ("customers", "accounts"),
        "Vypiš c.name a a.balance pomocí INNER JOIN. "
        "Použij aliasy customers c a accounts a, vazba je customer_id.",
        "SELECT c.name, a.balance FROM customers c INNER JOIN accounts a "
        "ON c.customer_id = a.customer_id;",
        "Začni FROM customers c INNER JOIN accounts a; v ON nejprve uveď c.customer_id.",
    ),
    _task(
        21, "intermediate", "write-query", ("accounts", "transactions"),
        "Pro každý účet včetně účtů bez transakcí vypiš a.account_id "
        "a COUNT(t.transaction_id) AS transaction_count. Použij LEFT JOIN, "
        "aliasy accounts a a transactions t, vazba je account_id.",
        "SELECT a.account_id, COUNT(t.transaction_id) AS transaction_count "
        "FROM accounts a LEFT JOIN transactions t ON a.account_id = t.account_id "
        "GROUP BY a.account_id;",
        "Po LEFT JOIN seskup podle a.account_id; nepočítej COUNT(*).",
    ),
    _task(
        22, "intermediate", "write-query", ("accounts",),
        "Vypiš branch_id a SUM(balance) AS total_balance pro pobočky se součtem "
        "zůstatků větším než 1000.",
        "SELECT branch_id, SUM(balance) AS total_balance FROM accounts "
        "GROUP BY branch_id HAVING SUM(balance) > 1000;",
        "Použij GROUP BY branch_id a HAVING SUM(balance) > 1000.",
    ),
    _task(
        23, "intermediate", "write-query", ("accounts",),
        "Vypiš account_id a CASE jako balance_band: při balance >= 1000 vrať HIGH, "
        "jinak LOW.",
        "SELECT account_id, CASE WHEN balance >= 1000 THEN 'HIGH' ELSE 'LOW' END "
        "AS balance_band FROM accounts;",
        "Použij CASE WHEN ... THEN ... ELSE ... END AS balance_band.",
    ),
    _task(
        24, "intermediate", "write-query", ("accounts",),
        "Vypiš account_id a ROW_NUMBER() AS position pro každý customer_id zvlášť. "
        "Uvnitř okna řaď podle balance DESC, account_id.",
        "SELECT account_id, ROW_NUMBER() OVER (PARTITION BY customer_id "
        "ORDER BY balance DESC, account_id) AS position FROM accounts;",
        "Oddíl okna urči PARTITION BY customer_id, pak přidej uvedené ORDER BY.",
    ),
    _task(
        25, "intermediate", "write-query", ("transactions",),
        "Vypiš transaction_id a průběžný součet amount AS running_amount "
        "pro každý account_id zvlášť. Řaď v okně podle transaction_id "
        "a použij ROWS UNBOUNDED PRECEDING.",
        "SELECT transaction_id, SUM(amount) OVER (PARTITION BY account_id "
        "ORDER BY transaction_id ROWS UNBOUNDED PRECEDING) AS running_amount "
        "FROM transactions;",
        "SUM(amount) OVER obsahuje PARTITION BY, ORDER BY a rámec ROWS.",
    ),
    _task(
        26, "intermediate", "find-bug", ("customers", "accounts"),
        "Oprav vazbu INNER JOIN zákazníků na jejich účty podle customer_id.",
        "SELECT c.name, a.account_id FROM customers c INNER JOIN accounts a "
        "ON c.customer_id = a.customer_id;",
        "account_id není identifikátor zákazníka.",
        sql="SELECT c.name, a.account_id FROM customers c INNER JOIN accounts a "
        "ON c.customer_id = a.account_id;",
    ),
    _task(
        27, "intermediate", "find-bug", ("accounts",),
        "Oprav filtr na součet skupiny; zachovej GROUP BY i mez 1000.",
        "SELECT branch_id, SUM(balance) FROM accounts GROUP BY branch_id "
        "HAVING SUM(balance) > 1000;",
        "Agregovaný součet filtruj pomocí HAVING až za GROUP BY.",
        sql="SELECT branch_id, SUM(balance) FROM accounts WHERE SUM(balance) > 1000 "
        "GROUP BY branch_id;",
    ),
    _task(
        28, "intermediate", "find-bug", ("accounts",),
        "Doplň chybějící seskupení; požadován je součet pro každý status.",
        "SELECT status, SUM(balance) FROM accounts GROUP BY status;",
        "Neagregovaný status musí být v GROUP BY.",
        sql="SELECT status, SUM(balance) FROM accounts;",
    ),
    _task(
        29, "intermediate", "find-bug", ("accounts",),
        "Oprav nedokončený výraz CASE; jiné části neměň.",
        "SELECT account_id, CASE WHEN balance > 0 THEN 'POSITIVE' ELSE 'OTHER' END "
        "AS balance_label FROM accounts;",
        "Výraz CASE končí slovem END před aliasem.",
        sql="SELECT account_id, CASE WHEN balance > 0 THEN 'POSITIVE' ELSE 'OTHER' "
        "AS balance_label FROM accounts;",
    ),
    _task(
        30, "intermediate", "find-bug", ("accounts", "transactions"),
        "Dotaz má zachovat i účty bez kreditních transakcí. Přesuň filtr "
        "t.kind do ON za vazbu pomocí AND a odstraň WHERE.",
        "SELECT a.account_id, t.amount FROM accounts a LEFT JOIN transactions t "
        "ON a.account_id = t.account_id AND t.kind = 'CREDIT';",
        "WHERE na pravé tabulce zahazuje řádky doplněné hodnotami NULL.",
        sql="SELECT a.account_id, t.amount FROM accounts a LEFT JOIN transactions t "
        "ON a.account_id = t.account_id WHERE t.kind = 'CREDIT';",
    ),
    _task(
        31, "intermediate", "find-bug", ("accounts",),
        "Dotaz má vybrat pouze aktivní účty se zůstatkem pod 0 nebo nad 1000. "
        "Oprav prioritu operátorů přidáním závorek kolem obou mezí.",
        "SELECT account_id FROM accounts WHERE status = 'ACTIVE' "
        "AND (balance < 0 OR balance > 1000);",
        "AND má vyšší prioritu než OR.",
        sql="SELECT account_id FROM accounts WHERE status = 'ACTIVE' "
        "AND balance < 0 OR balance > 1000;",
    ),
    _task(
        32, "intermediate", "explain-result", ("customers", "accounts"),
        "Jaká jména a zůstatky vrátí spojení? Pořadí řádků není zaručeno.",
        "Spojení vrátí Adam Novak se zůstatkem 1500 a Eva Mala se zůstatkem 500.",
        "Každý zákazník má v ukázce právě jeden účet.",
        sql="SELECT c.name, a.balance FROM customers c INNER JOIN accounts a "
        "ON c.customer_id = a.customer_id;",
        keywords=("adam novak", "1500", "eva mala", "500"),
    ),
    _task(
        33, "intermediate", "explain-result", ("accounts", "transactions"),
        "Jaké počty transakcí vrátí dotaz pro účty 10 a 20? Vysvětli nulu.",
        "Účet 10 má 2 transakce; účet 20 má 0, protože COUNT ignoruje NULL.",
        "LEFT JOIN zachová účet bez transakcí.",
        sql="SELECT a.account_id, COUNT(t.transaction_id) AS transaction_count "
        "FROM accounts a LEFT JOIN transactions t ON a.account_id = t.account_id "
        "GROUP BY a.account_id ORDER BY a.account_id;",
        keywords=("2 transakce", "0", "null"),
    ),
    _task(
        34, "intermediate", "explain-result", ("accounts",),
        "Která pobočka projde HAVING a jaký má součet?",
        "Pobočka 1 má součet 1500 a jako jediná projde filtrem.",
        "Pobočka 2 má pouze 500.",
        sql="SELECT branch_id, SUM(balance) AS total_balance FROM accounts "
        "GROUP BY branch_id HAVING SUM(balance) > 1000;",
        keywords=("pobočka 1", "1500"),
    ),
    _task(
        35, "intermediate", "explain-result", ("accounts",),
        "Jaká pořadí přidělí RANK účtům 10 a 20? Zmiň obě pořadí.",
        "Účet 10 má pořadí 1, účet 20 má pořadí 2 podle sestupného zůstatku.",
        "RANK řadí nejvyšší balance jako první; shody by sdílely pořadí.",
        sql="SELECT account_id, RANK() OVER (ORDER BY balance DESC) AS balance_rank "
        "FROM accounts ORDER BY account_id;",
        keywords=("pořadí 1", "pořadí 2", "sestup"),
    ),
    _task(
        36, "intermediate", "explain-result", ("transactions",),
        "Jaký průběžný součet mají transakce 100 a 101?",
        "Transakce 100 má průběžný součet 200; transakce 101 má součet 150.",
        "Druhá transakce odečítá 50 od prvního součtu.",
        sql="SELECT transaction_id, SUM(amount) OVER (PARTITION BY account_id "
        "ORDER BY transaction_id ROWS UNBOUNDED PRECEDING) AS running_amount "
        "FROM transactions ORDER BY transaction_id;",
        keywords=("200", "150", "součet"),
    ),
    # Advanced: korelace, více vazeb, Oracle regex a jemné chyby oken.
    _task(
        37, "advanced", "write-query", ("customers", "loans"),
        "Vypiš c.name zákazníků bez schváleného úvěru pomocí NOT EXISTS. "
        "Použij customers c a v poddotazu SELECT 1 FROM loans l; "
        "vazbu l.customer_id = c.customer_id uveď před filtrem status APPROVED.",
        "SELECT c.name FROM customers c WHERE NOT EXISTS "
        "(SELECT 1 FROM loans l WHERE l.customer_id = c.customer_id "
        "AND l.status = 'APPROVED');",
        "NOT EXISTS testuje nepřítomnost schváleného úvěru daného zákazníka.",
    ),
    _task(
        38, "advanced", "write-query", ("accounts", "transactions"),
        "Vypiš a.account_id účtů, jejichž balance je větší než čistý součet jejich "
        "transakcí; účet bez transakcí má součet 0. Použij korelovaný skalární "
        "poddotaz SUM(t.amount), NVL kolem celého poddotazu a aliasy accounts a, transactions t.",
        "SELECT a.account_id FROM accounts a WHERE a.balance > "
        "NVL((SELECT SUM(t.amount) FROM transactions t "
        "WHERE t.account_id = a.account_id), 0);",
        "Porovnej a.balance > NVL((SELECT SUM(...) ...), 0).",
    ),
    _task(
        39, "advanced", "write-query", ("customers", "accounts", "branches"),
        "Vypiš c.name AS customer_name, b.name AS branch_name a a.balance "
        "aktivních účtů. Spoj postupně customers c, accounts a a branches b "
        "pomocí INNER JOIN. Vazby: c.customer_id = a.customer_id, "
        "a.branch_id = b.branch_id. Filtruj a.status = 'ACTIVE'.",
        "SELECT c.name AS customer_name, b.name AS branch_name, a.balance "
        "FROM customers c INNER JOIN accounts a ON c.customer_id = a.customer_id "
        "INNER JOIN branches b ON a.branch_id = b.branch_id WHERE a.status = 'ACTIVE';",
        "Za druhým ON následuje WHERE s filtrem aktivních účtů.",
    ),
    _task(
        40, "advanced", "write-query", ("transactions",),
        "Vypiš transaction_id a předchozí amount AS previous_amount pomocí "
        "LAG(amount). Odděl účty podle account_id a v okně řaď podle transaction_id.",
        "SELECT transaction_id, LAG(amount) OVER (PARTITION BY account_id "
        "ORDER BY transaction_id) AS previous_amount FROM transactions;",
        "Použij LAG(amount) OVER (PARTITION BY account_id ORDER BY transaction_id).",
    ),
    _task(
        41, "advanced", "write-query", ("accounts",),
        "Vypiš account_id a husté pořadí zůstatků AS balance_rank "
        "pomocí DENSE_RANK(), v okně řaď podle balance DESC.",
        "SELECT account_id, DENSE_RANK() OVER (ORDER BY balance DESC) AS balance_rank "
        "FROM accounts;",
        "DENSE_RANK nevytváří mezery v pořadí při shodných zůstatcích.",
    ),
    _task(
        42, "advanced", "write-query", ("customers",),
        "Vypiš customer_id a doménu e-mailu AS email_domain pomocí "
        "REGEXP_SUBSTR(email, '[^@]+$'). Chybějící e-mail ponech jako NULL.",
        "SELECT customer_id, REGEXP_SUBSTR(email, '[^@]+$') AS email_domain "
        "FROM customers;",
        "Vzor [^@]+$ vybere závěrečnou část bez zavináče.",
    ),
    _task(
        43, "advanced", "find-bug", ("customers", "loans"),
        "Poddotaz má hledat schválený úvěr právě vnějšího zákazníka. "
        "Oprav pravou stranu korelační podmínky.",
        "SELECT c.name FROM customers c WHERE NOT EXISTS "
        "(SELECT 1 FROM loans l WHERE l.customer_id = c.customer_id "
        "AND l.status = 'APPROVED');",
        "l.customer_id = l.customer_id není korelace na customers c.",
        sql="SELECT c.name FROM customers c WHERE NOT EXISTS "
        "(SELECT 1 FROM loans l WHERE l.customer_id = l.customer_id "
        "AND l.status = 'APPROVED');",
    ),
    _task(
        44, "advanced", "find-bug", ("transactions",),
        "Předchozí částka nesmí pocházet z jiného účtu. Doplň oddíl okna, "
        "jinak dotaz neměň.",
        "SELECT transaction_id, LAG(amount) OVER (PARTITION BY account_id "
        "ORDER BY transaction_id) AS previous_amount FROM transactions;",
        "Před ORDER BY přidej PARTITION BY account_id.",
        sql="SELECT transaction_id, LAG(amount) OVER (ORDER BY transaction_id) "
        "AS previous_amount FROM transactions;",
    ),
    _task(
        45, "advanced", "find-bug", ("transactions",),
        "Součet má růst po jednotlivých transakcích, i když mají stejný booked_on. "
        "Za booked_on doplň transaction_id a explicitní ROWS UNBOUNDED PRECEDING.",
        "SELECT transaction_id, SUM(amount) OVER (PARTITION BY account_id "
        "ORDER BY booked_on, transaction_id ROWS UNBOUNDED PRECEDING) "
        "AS running_amount FROM transactions;",
        "Výchozí RANGE zahrnuje všechny řádky se stejnou hodnotou řazení najednou.",
        sql="SELECT transaction_id, SUM(amount) OVER (PARTITION BY account_id "
        "ORDER BY booked_on) AS running_amount FROM transactions;",
    ),
    _task(
        46, "advanced", "find-bug", ("accounts", "transactions"),
        "Dotaz má vrátit všechny účty s čistým součtem transakcí, "
        "pro účty bez transakcí 0. Nahraď SUM(t.amount) výrazem NVL(SUM(t.amount), 0).",
        "SELECT a.account_id, NVL(SUM(t.amount), 0) AS net_amount FROM accounts a "
        "LEFT JOIN transactions t ON a.account_id = t.account_id GROUP BY a.account_id;",
        "SUM nad samými NULL vrací NULL, nikoli 0.",
        sql="SELECT a.account_id, SUM(t.amount) AS net_amount FROM accounts a "
        "LEFT JOIN transactions t ON a.account_id = t.account_id GROUP BY a.account_id;",
    ),
    _task(
        47, "advanced", "find-bug", ("customers",),
        "Dotaz má vybrat e-maily končící přesně doménou example.test. "
        "Oprav pouze regex: přidej ^ na začátek a escapuj tečku v doméně.",
        r"SELECT name FROM customers WHERE REGEXP_LIKE(email, '^[^@]+@example\.test$');",
        r"Tečka v regexu znamená libovolný znak; doslovná tečka se píše \.",
        sql="SELECT name FROM customers WHERE REGEXP_LIKE(email, '[^@]+@example.test$');",
    ),
    _task(
        48, "advanced", "find-bug", ("accounts",),
        "V Oracle nelze filtrovat analytický alias v témže WHERE. "
        "Přesuň výpočet do inline view bez aliasu tabulky a vně vyber account_id "
        "s balance_rank = 1. Zachovej DENSE_RANK i jeho řazení.",
        "SELECT account_id FROM (SELECT account_id, DENSE_RANK() OVER "
        "(ORDER BY balance DESC) AS balance_rank FROM accounts) WHERE balance_rank = 1;",
        "Vnější SELECT account_id čte z (SELECT account_id, DENSE_RANK() ...).",
        sql="SELECT account_id, DENSE_RANK() OVER (ORDER BY balance DESC) AS balance_rank "
        "FROM accounts WHERE balance_rank = 1;",
    ),
    _task(
        49, "advanced", "explain-result", ("customers", "loans"),
        "Který zákazník nemá schválený úvěr? Vysvětli vliv stavu PENDING.",
        "Vrátí Eva Mala; její úvěr je PENDING, nikoli schválený.",
        "NOT EXISTS hledá absenci úvěru se stavem APPROVED, ne absenci všech úvěrů.",
        sql="SELECT c.name FROM customers c WHERE NOT EXISTS "
        "(SELECT 1 FROM loans l WHERE l.customer_id = c.customer_id "
        "AND l.status = 'APPROVED');",
        keywords=("eva mala", "pending", "schválený"),
    ),
    _task(
        50, "advanced", "explain-result", ("transactions",),
        "Jakou následující částku vrátí LEAD pro transakce 100 a 101? "
        "Uveď i chybějící hodnotu.",
        "Transakce 100 má následující částku -50; transakce 101 má NULL.",
        "LEAD čte následující řádek uvnitř stejného účtu.",
        sql="SELECT transaction_id, LEAD(amount) OVER (PARTITION BY account_id "
        "ORDER BY transaction_id) AS next_amount FROM transactions ORDER BY transaction_id;",
        keywords=("-50", "null", "následující"),
    ),
    _task(
        51, "advanced", "explain-result", ("accounts",),
        "Který účet má husté pořadí 2 a proč? Co by se stalo s pořadím při shodách?",
        "Účet 20 má druhý nejvyšší zůstatek 500. Shody sdílejí pořadí bez mezer.",
        "DENSE_RANK při shodách nevynechává následující pořadí.",
        sql="SELECT account_id FROM (SELECT account_id, DENSE_RANK() OVER "
        "(ORDER BY balance DESC) AS balance_rank FROM accounts) WHERE balance_rank = 2;",
        keywords=("20", "500", "bez mezer"),
    ),
    _task(
        52, "advanced", "explain-result", ("customers",),
        "Jaké příjmení vrátí regex pro každého zákazníka? Popiš význam vzoru.",
        "Vrátí Novak a Mala; regex vybírá poslední slovo jména.",
        "Vzor [^ ]+$ hledá závěrečný úsek bez mezer.",
        sql="SELECT customer_id, REGEXP_SUBSTR(name, '[^ ]+$') AS surname FROM customers;",
        keywords=("novak", "mala", "poslední"),
    ),
    _task(
        53, "advanced", "explain-result", ("branches", "accounts", "transactions"),
        "Jaké čisté částky vrátí report pro pobočky Central a South? "
        "Vysvětli zachování pobočky bez transakcí.",
        "Central má čistou částku 150. South má 0, protože LEFT JOIN ji zachová "
        "a NVL nahradí NULL nulou.",
        "Dvě transakce účtu 10 dávají 200 - 50; pobočka 2 nemá žádnou.",
        sql="SELECT b.name, NVL(SUM(t.amount), 0) AS net_amount FROM branches b "
        "LEFT JOIN accounts a ON b.branch_id = a.branch_id "
        "LEFT JOIN transactions t ON a.account_id = t.account_id "
        "GROUP BY b.branch_id, b.name;",
        keywords=("150", "south", "0", "left join"),
    ),
    _task(
        54, "advanced", "explain-result", ("transactions",),
        "Jaký součet vrátí okno pro každý řádek a proč se hodnoty shodují? "
        "Obě transakce mají stejný den.",
        "Oba řádky mají součet 150; RANGE zahrne všechny transakce se stejným datem.",
        "RANGE pracuje s hodnotou řazení, ne s jednotlivými fyzickými řádky.",
        sql="SELECT transaction_id, SUM(amount) OVER (PARTITION BY account_id "
        "ORDER BY booked_on RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) "
        "AS day_total FROM transactions;",
        keywords=("150", "range", "stejným datem"),
    ),
]


def get_random_task(difficulty, task_type):
    filtered = [
        task for task in TASKS
        if task["difficulty"] == difficulty and task["type"] == task_type
    ]

    if not filtered:
        return None

    return random.choice(filtered)
