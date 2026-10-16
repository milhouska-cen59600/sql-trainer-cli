# sql-trainer-cli
CLI app for practicing SQL tasks and learning Git, GitHub and VS Code

## Katalog úloh

Katalog obsahuje 54 českých úloh pro Oracle SQL v bankovní doméně:
18 pro každou úroveň a vždy 6 úloh každého typu (`write-query`, `find-bug`,
`explain-result`). Každá použitá tabulka má v zadání dvě ukázkové řádky
v zarovnané ASCII tabulce; názvy tabulek a sloupců jsou anglické.

- **Beginner:** výběr sloupců, WHERE, AND, ORDER BY, BETWEEN, IN, LIKE,
  NULL, DISTINCT, COUNT, SUM a AVG.
- **Intermediate:** INNER/LEFT JOIN, aliasy, GROUP BY/HAVING, CASE,
  priorita podmínek, ROW_NUMBER, RANK a průběžné součty.
- **Advanced:** NOT EXISTS, korelované poddotazy, spojení více tabulek,
  LAG/LEAD, DENSE_RANK, REGEXP_SUBSTR/REGEXP_LIKE, NVL,
  rozdíly rámců ROWS/RANGE a bankovní reporty.

Spuštění: `python app.py`, poté `/start`.
U `write-query` i `find-bug` se zadává celý SQL dotaz. Kontrola používá
tokenovou normalizaci shodnou s `SQLTrainerGUI.normalize_sql` ve větvi
`feature/oracle-task-expansion`, nikoli databázový engine: ignoruje velikost
písmen mimo textové literály, mezery mezi tokeny (včetně interpunkce) a jeden
koncový středník. Obsah textových literálů včetně velikosti písmen a mezer
musí odpovídat přesně. Jiné ekvivalentní zápisy
nemusí přijmout; očekávané aliasy a tvar dotazu upřesňuje zadání a nápověda.
U `explain-result` se zadává české vysvětlení a kontrolují se klíčová slova.
Stačí dvě shody; nejde o úplnou kontrolu významu odpovědi. Číselná klíčová
slova se hledají jako celé hodnoty včetně znaménka a desetinné části,
nikoli jako podřetězce jiných čísel. Textová klíčová slova mohou odpovídat
i části slova, aby se zachovalo rozpoznávání českých slovních kmenů.
Příkazy `/hint` a `/solution` zobrazí nápovědu a vzorovou odpověď.
Každá načtená úloha se započítá pouze při první neprázdné odpovědi, ať už je
správná nebo chybná. Další odpovědi skóre nemění; `/next` nebo nový výběr
přes `/start` načte novou úlohu s novým pokusem.

Testy: `python -m unittest discover -v`. Kontrolují kontrakt a rozložení úloh,
ASCII tabulky, vyhodnocování odpovědí i výsledky všech dotazů nad ukázkovými
daty. Výsledky ověřují pomocí SQLite a náhrad použitých skalárních funkcí
Oracle; nenahrazují integrační test proti Oracle.
