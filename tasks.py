import random
from copy import deepcopy


TASKS = [{'id': 1,
  'difficulty': 'beginner',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Bankovní poradce potřebuje vypsat všechny klienty, jejichž mesicni_prijem je vyšší '
            'než 20000 Kč.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni, mesto, mesicni_prijem\n'
            '\n'
            'Napiš SQL dotaz, který vrátí všechny sloupce těchto klientů.',
  'sql': None,
  'hint': 'Použij SELECT * FROM klienti a WHERE mesicni_prijem > 20000.',
  'solution': 'SELECT * FROM klienti WHERE mesicni_prijem > 20000;',
  'expected_answer': 'SELECT * FROM klienti WHERE mesicni_prijem > 20000;',
  'keywords': []},
 {'id': 2,
  'difficulty': 'beginner',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ získat čísla účtů a jejich zůstatky pro všechny účty, kde je zustatek '
            'vyšší než 100000 Kč.\n'
            '\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek\n'
            '\n'
            'Vrať pouze sloupce cislo_uctu a zustatek v tomto pořadí.',
  'sql': None,
  'hint': 'Vyber jen dva sloupce a použij WHERE zustatek > 100000.',
  'solution': 'SELECT cislo_uctu, zustatek FROM ucty WHERE zustatek > 100000;',
  'expected_answer': 'SELECT cislo_uctu, zustatek FROM ucty WHERE zustatek > 100000;',
  'keywords': []},
 {'id': 3,
  'difficulty': 'beginner',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            "Potřebuješ vypsat všechny transakce typu 'VYBER'.\n"
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, typ, poznamka\n'
            '\n'
            'Napiš SQL dotaz, který vrátí všechny sloupce transakcí typu VYBER.',
  'sql': None,
  'hint': "Použij WHERE typ = 'VYBER'.",
  'solution': "SELECT * FROM transakce WHERE typ = 'VYBER';",
  'expected_answer': "SELECT * FROM transakce WHERE typ = 'VYBER';",
  'keywords': []},
 {'id': 4,
  'difficulty': 'beginner',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má vypsat jména klientů z města Praha, ale obsahuje chybu.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni, mesto\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT jmeno FROM klienti WHERE mesto = Praha;',
  'hint': 'Textové hodnoty musí být v SQL uzavřené do jednoduchých uvozovek.',
  'solution': "SELECT jmeno FROM klienti WHERE mesto = 'Praha';",
  'expected_answer': "SELECT jmeno FROM klienti WHERE mesto = 'Praha';",
  'keywords': []},
 {'id': 5,
  'difficulty': 'beginner',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má vrátit čísla účtů se zůstatkem vyšším než 50000 Kč, ale je v něm překlep.\n'
            '\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT cislo_uctu FORM ucty WHERE zustatek > 50000;',
  'hint': 'Zkontroluj správný zápis klauzule FROM.',
  'solution': 'SELECT cislo_uctu FROM ucty WHERE zustatek > 50000;',
  'expected_answer': 'SELECT cislo_uctu FROM ucty WHERE zustatek > 50000;',
  'keywords': []},
 {'id': 6,
  'difficulty': 'beginner',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má vrátit všechny úvěry s úrokovou sazbou vyšší než 5, ale používá chybný název '
            'sloupce.\n'
            '\n'
            'Tabulka: uvery\n'
            'Sloupce: id, klient_id, castka_uveru, urokova_sazba, stav\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT * FROM uvery WHERE urok > 5;',
  'hint': 'Zkontroluj přesný název sloupce s úrokovou sazbou.',
  'solution': 'SELECT * FROM uvery WHERE urokova_sazba > 5;',
  'expected_answer': 'SELECT * FROM uvery WHERE urokova_sazba > 5;',
  'keywords': []},
 {'id': 7,
  'difficulty': 'beginner',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni, mesto, mesicni_prijem',
  'sql': 'SELECT * FROM klienti WHERE mesicni_prijem > 30000;',
  'hint': 'Zaměř se na podmínku WHERE a na to, že SELECT * vrací všechny sloupce.',
  'solution': 'Dotaz vrátí všechny sloupce všech klientů, jejichž měsíční příjem je vyšší než '
              '30000 Kč.',
  'expected_answer': 'Dotaz vrátí všechny klienty s měsíčním příjmem vyšším než 30000 Kč.',
  'keywords': ['klient', 'příjm', 'vyšším', '30000']},
 {'id': 8,
  'difficulty': 'beginner',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, typ, poznamka',
  'sql': 'SELECT * FROM transakce WHERE castka > 10000;',
  'hint': 'Zaměř se na podmínku WHERE a na filtraci podle castka.',
  'solution': 'Dotaz vrátí všechny transakce, jejichž částka je vyšší než 10000.',
  'expected_answer': 'Dotaz vrátí transakce s částkou vyšší než 10000.',
  'keywords': ['transakce', 'částk', 'vyšší', '10000']},
 {'id': 9,
  'difficulty': 'beginner',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek',
  'sql': 'SELECT cislo_uctu, zustatek FROM ucty WHERE zustatek < 0;',
  'hint': 'Zaměř se na výběr konkrétních sloupců a podmínku se záporným zůstatkem.',
  'solution': 'Dotaz vrátí čísla účtů a jejich zůstatky pro účty, které mají záporný zůstatek.',
  'expected_answer': 'Dotaz vrátí čísla účtů a zůstatky účtů se záporným zůstatkem.',
  'keywords': ['čísla účtů', 'zůstat', 'záporn']},
 {'id': 10,
  'difficulty': 'intermediate',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ vypsat jména klientů a čísla jejich účtů.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni\n'
            '\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek\n'
            '\n'
            'Vztah: ucty.klient_id = klienti.id\n'
            '\n'
            'Napiš SQL dotaz, který vrátí sloupce jmeno, prijmeni a cislo_uctu.',
  'sql': None,
  'hint': 'Použij JOIN mezi tabulkami klienti a ucty přes klienti.id = ucty.klient_id.',
  'solution': 'SELECT k.jmeno, k.prijmeni, u.cislo_uctu FROM klienti k JOIN ucty u ON k.id = '
              'u.klient_id;',
  'expected_answer': 'SELECT k.jmeno, k.prijmeni, u.cislo_uctu FROM klienti k JOIN ucty u ON k.id '
                     '= u.klient_id;',
  'keywords': []},
 {'id': 11,
  'difficulty': 'intermediate',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ očíslovat transakce každého účtu od nejnovější po nejstarší.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, typ\n'
            '\n'
            'Napiš SQL dotaz, který vrátí sloupce ucet_id, datum_transakce, castka a navíc pořadí '
            'transakce v rámci účtu pomocí ROW_NUMBER(). Použij alias poradi.',
  'sql': None,
  'hint': 'Použij ROW_NUMBER() OVER (PARTITION BY ucet_id ORDER BY datum_transakce DESC).',
  'solution': 'SELECT ucet_id, datum_transakce, castka, ROW_NUMBER() OVER (PARTITION BY ucet_id '
              'ORDER BY datum_transakce DESC) AS poradi FROM transakce;',
  'expected_answer': 'SELECT ucet_id, datum_transakce, castka, ROW_NUMBER() OVER (PARTITION BY '
                     'ucet_id ORDER BY datum_transakce DESC) AS poradi FROM transakce;',
  'keywords': []},
 {'id': 12,
  'difficulty': 'intermediate',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ u každé transakce zobrazit také celkovou částku transakcí na stejném '
            'účtu.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, typ\n'
            '\n'
            'Napiš SQL dotaz, který vrátí sloupce id, ucet_id, castka a součet castka v rámci '
            'stejného ucet_id pomocí analytické funkce. Použij alias soucet_na_uctu.',
  'sql': None,
  'hint': 'Použij SUM(castka) OVER (PARTITION BY ucet_id).',
  'solution': 'SELECT id, ucet_id, castka, SUM(castka) OVER (PARTITION BY ucet_id) AS '
              'soucet_na_uctu FROM transakce;',
  'expected_answer': 'SELECT id, ucet_id, castka, SUM(castka) OVER (PARTITION BY ucet_id) AS '
                     'soucet_na_uctu FROM transakce;',
  'keywords': []},
 {'id': 13,
  'difficulty': 'intermediate',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má vrátit jméno klienta a číslo účtu, ale obsahuje chybu v podmínce JOIN.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT k.jmeno, u.cislo_uctu FROM klienti k JOIN ucty u ON k.id = u.id;',
  'hint': 'Účet se neváže přes své vlastní id, ale přes klient_id.',
  'solution': 'SELECT k.jmeno, u.cislo_uctu FROM klienti k JOIN ucty u ON k.id = u.klient_id;',
  'expected_answer': 'SELECT k.jmeno, u.cislo_uctu FROM klienti k JOIN ucty u ON k.id = '
                     'u.klient_id;',
  'keywords': []},
 {'id': 14,
  'difficulty': 'intermediate',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má spočítat počet účtů každého klienta, ale používá chybnou klauzuli.\n'
            '\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT klient_id, COUNT(*) FROM ucty;',
  'hint': 'Pokud používáš COUNT(*) spolu s klient_id, musíš seskupovat podle klient_id.',
  'solution': 'SELECT klient_id, COUNT(*) FROM ucty GROUP BY klient_id;',
  'expected_answer': 'SELECT klient_id, COUNT(*) FROM ucty GROUP BY klient_id;',
  'keywords': []},
 {'id': 15,
  'difficulty': 'intermediate',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má očíslovat transakce podle data v rámci účtu, ale obsahuje chybu v analytické '
            'funkci.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT ucet_id, datum_transakce, ROW_NUMBER() OVER (ORDER BY datum_transakce DESC) AS '
         'poradi FROM transakce;',
  'hint': 'Pořadí se má počítat zvlášť pro každý účet.',
  'solution': 'SELECT ucet_id, datum_transakce, ROW_NUMBER() OVER (PARTITION BY ucet_id ORDER BY '
              'datum_transakce DESC) AS poradi FROM transakce;',
  'expected_answer': 'SELECT ucet_id, datum_transakce, ROW_NUMBER() OVER (PARTITION BY ucet_id '
                     'ORDER BY datum_transakce DESC) AS poradi FROM transakce;',
  'keywords': []},
 {'id': 16,
  'difficulty': 'intermediate',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu, zustatek\n'
            'Vztah: ucty.klient_id = klienti.id',
  'sql': 'SELECT k.jmeno, k.prijmeni, u.cislo_uctu FROM klienti k JOIN ucty u ON k.id = '
         'u.klient_id;',
  'hint': 'Zaměř se na to, že JOIN spojuje klienty s jejich účty.',
  'solution': 'Dotaz vrátí jména a příjmení klientů spolu s čísly jejich účtů.',
  'expected_answer': 'Dotaz vrátí klienty a čísla jejich účtů.',
  'keywords': ['klient', 'čísla', 'účtů']},
 {'id': 17,
  'difficulty': 'intermediate',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka',
  'sql': 'SELECT ucet_id, castka, SUM(castka) OVER (PARTITION BY ucet_id) AS soucet_na_uctu FROM '
         'transakce;',
  'hint': 'Analytická funkce SUM OVER neslučuje řádky, jen doplní vypočtenou hodnotu ke každému '
          'řádku.',
  'solution': 'Dotaz vrátí každou transakci a u každé zároveň zobrazí celkový součet částek všech '
              'transakcí na stejném účtu.',
  'expected_answer': 'Dotaz vrátí transakce a u každé zobrazí celkový součet transakcí stejného '
                     'účtu.',
  'keywords': ['transakce', 'součet', 'účtu', 'každé']},
 {'id': 18,
  'difficulty': 'intermediate',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka',
  'sql': 'SELECT ucet_id, datum_transakce, ROW_NUMBER() OVER (PARTITION BY ucet_id ORDER BY '
         'datum_transakce DESC) AS poradi FROM transakce;',
  'hint': 'ROW_NUMBER čísluje řádky v rámci skupiny definované PARTITION BY.',
  'solution': 'Dotaz vrátí transakce a každé přiřadí pořadí v rámci jejího účtu od nejnovější po '
              'nejstarší.',
  'expected_answer': 'Dotaz očísluje transakce v rámci každého účtu od nejnovější po nejstarší.',
  'keywords': ['očísluje', 'účtu', 'nejnovější']},
 {'id': 19,
  'difficulty': 'advanced',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ vypsat jméno klienta, číslo účtu a částku transakce pro všechny transakce '
            'vyšší než 50000 Kč.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, typ\n'
            '\n'
            'Vztahy:\n'
            '- ucty.klient_id = klienti.id\n'
            '- transakce.ucet_id = ucty.id\n'
            '\n'
            'Napiš SQL dotaz, který vrátí sloupce k.jmeno, u.cislo_uctu a t.castka.',
  'sql': None,
  'hint': 'Budeš potřebovat spojit tři tabulky a filtrovat podle t.castka > 50000.',
  'solution': 'SELECT k.jmeno, u.cislo_uctu, t.castka FROM klienti k JOIN ucty u ON k.id = '
              'u.klient_id JOIN transakce t ON u.id = t.ucet_id WHERE t.castka > 50000;',
  'expected_answer': 'SELECT k.jmeno, u.cislo_uctu, t.castka FROM klienti k JOIN ucty u ON k.id = '
                     'u.klient_id JOIN transakce t ON u.id = t.ucet_id WHERE t.castka > 50000;',
  'keywords': []},
 {'id': 20,
  'difficulty': 'advanced',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ u každé transakce zobrazit také částku předchozí transakce na stejném účtu '
            'podle data.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka\n'
            '\n'
            'Napiš SQL dotaz, který vrátí sloupce ucet_id, datum_transakce, castka a předchozí '
            'castka pomocí LAG(). Použij alias predchozi_castka.',
  'sql': None,
  'hint': 'Použij LAG(castka) OVER (PARTITION BY ucet_id ORDER BY datum_transakce).',
  'solution': 'SELECT ucet_id, datum_transakce, castka, LAG(castka) OVER (PARTITION BY ucet_id '
              'ORDER BY datum_transakce) AS predchozi_castka FROM transakce;',
  'expected_answer': 'SELECT ucet_id, datum_transakce, castka, LAG(castka) OVER (PARTITION BY '
                     'ucet_id ORDER BY datum_transakce) AS predchozi_castka FROM transakce;',
  'keywords': []},
 {'id': 21,
  'difficulty': 'advanced',
  'type': 'write-query',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Potřebuješ najít všechny transakce, jejichž poznamka začíná textem VS: následovaným '
            'přesně šesti číslicemi.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, typ, poznamka\n'
            '\n'
            'Napiš SQL dotaz, který vrátí všechny sloupce takových transakcí pomocí Oracle funkce '
            'REGEXP_LIKE.',
  'sql': None,
  'hint': "Použij REGEXP_LIKE(poznamka, '^VS:[0-9]{6}$').",
  'solution': "SELECT * FROM transakce WHERE REGEXP_LIKE(poznamka, '^VS:[0-9]{6}$');",
  'expected_answer': "SELECT * FROM transakce WHERE REGEXP_LIKE(poznamka, '^VS:[0-9]{6}$');",
  'keywords': []},
 {'id': 22,
  'difficulty': 'advanced',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má vrátit jméno klienta a částku transakce pro transakce nad 50000 Kč, ale '
            'obsahuje chybu v jednom z JOINů.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno, prijmeni\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT k.jmeno, t.castka FROM klienti k JOIN ucty u ON k.id = u.klient_id JOIN transakce '
         't ON k.id = t.ucet_id WHERE t.castka > 50000;',
  'hint': 'Transakce se váže na účet, ne přímo na klienta.',
  'solution': 'SELECT k.jmeno, t.castka FROM klienti k JOIN ucty u ON k.id = u.klient_id JOIN '
              'transakce t ON u.id = t.ucet_id WHERE t.castka > 50000;',
  'expected_answer': 'SELECT k.jmeno, t.castka FROM klienti k JOIN ucty u ON k.id = u.klient_id '
                     'JOIN transakce t ON u.id = t.ucet_id WHERE t.castka > 50000;',
  'keywords': []},
 {'id': 23,
  'difficulty': 'advanced',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má vrátit předchozí částku transakce na stejném účtu, ale obsahuje chybu v '
            'analytické funkci.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': 'SELECT ucet_id, datum_transakce, castka, LAG(castka) OVER (ORDER BY datum_transakce) AS '
         'predchozi_castka FROM transakce;',
  'hint': 'Předchozí transakce se má hledat v rámci stejného účtu.',
  'solution': 'SELECT ucet_id, datum_transakce, castka, LAG(castka) OVER (PARTITION BY ucet_id '
              'ORDER BY datum_transakce) AS predchozi_castka FROM transakce;',
  'expected_answer': 'SELECT ucet_id, datum_transakce, castka, LAG(castka) OVER (PARTITION BY '
                     'ucet_id ORDER BY datum_transakce) AS predchozi_castka FROM transakce;',
  'keywords': []},
 {'id': 24,
  'difficulty': 'advanced',
  'type': 'find-bug',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Dotaz má najít poznámky začínající VS: a šesti číslicemi, ale obsahuje chybu v '
            'regulárním výrazu.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, poznamka\n'
            '\n'
            'Oprav SQL dotaz přímo v editoru.',
  'sql': "SELECT * FROM transakce WHERE REGEXP_LIKE(poznamka, '^VS:[0-9]{5}$');",
  'hint': 'Po VS: má být přesně šest číslic, ne pět.',
  'solution': "SELECT * FROM transakce WHERE REGEXP_LIKE(poznamka, '^VS:[0-9]{6}$');",
  'expected_answer': "SELECT * FROM transakce WHERE REGEXP_LIKE(poznamka, '^VS:[0-9]{6}$');",
  'keywords': []},
 {'id': 25,
  'difficulty': 'advanced',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka',
  'sql': 'SELECT ucet_id, datum_transakce, castka, LAG(castka) OVER (PARTITION BY ucet_id ORDER BY '
         'datum_transakce) AS predchozi_castka FROM transakce;',
  'hint': 'LAG vrací hodnotu z předchozího řádku v rámci stejné skupiny.',
  'solution': 'Dotaz vrátí každou transakci a k ní také částku předchozí transakce na stejném účtu '
              'podle data.',
  'expected_answer': 'Dotaz vrátí transakce a u každé zobrazí částku předchozí transakce stejného '
                     'účtu.',
  'keywords': ['transakce', 'předchozí', 'účtu']},
 {'id': 26,
  'difficulty': 'advanced',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, datum_transakce, castka, poznamka',
  'sql': "SELECT * FROM transakce WHERE REGEXP_LIKE(poznamka, '^VS:[0-9]{6}$');",
  'hint': 'Zaměř se na to, jaký textový vzor regulární výraz hledá.',
  'solution': 'Dotaz vrátí transakce, jejichž poznámka přesně odpovídá formátu VS: následovanému '
              'šesti číslicemi.',
  'expected_answer': 'Dotaz vrátí transakce s poznámkou ve formátu VS: a šesti číslic.',
  'keywords': ['poznám', 'vs:', 'šesti', 'číslic']},
 {'id': 27,
  'difficulty': 'advanced',
  'type': 'explain-result',
  'prompt': 'Pracuješ v Oracle databázi.\n'
            '\n'
            'Vysvětli, co vrátí následující SQL dotaz.\n'
            '\n'
            'Tabulka: klienti\n'
            'Sloupce: id, jmeno\n'
            'Tabulka: ucty\n'
            'Sloupce: id, klient_id, cislo_uctu\n'
            'Tabulka: transakce\n'
            'Sloupce: id, ucet_id, castka\n'
            '\n'
            'Vztahy:\n'
            '- ucty.klient_id = klienti.id\n'
            '- transakce.ucet_id = ucty.id',
  'sql': 'SELECT k.jmeno, u.cislo_uctu, t.castka FROM klienti k JOIN ucty u ON k.id = u.klient_id '
         'JOIN transakce t ON u.id = t.ucet_id WHERE t.castka > 50000;',
  'hint': 'Zaměř se na spojení tří tabulek a filtr podle výše transakce.',
  'solution': 'Dotaz vrátí jméno klienta, číslo jeho účtu a částku transakce pro všechny transakce '
              'vyšší než 50000 Kč.',
  'expected_answer': 'Dotaz vrátí klienta, číslo účtu a částku transakcí vyšších než 50000 Kč.',
  'keywords': ['klient', 'číslo účtu', 'transakc', '50000']}]


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
