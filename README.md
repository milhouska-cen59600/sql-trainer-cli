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

## Webová verze (GitHub Pages)

Vedle nezměněného CLI (`python app.py`) a desktopového GUI
(`python gui_app.py`) je ve složce `web/` samostatná statická aplikace
v HTML/CSS/JavaScriptu. Nepotřebuje backend, databázi ani instalaci JS balíčků.
Nabízí všech 54 úloh, výběr Junior/Medior/Senior (odpovídá
beginner/intermediate/advanced), všechny tři typy, kontrolu odpovědi,
nápovědu, řešení, další úlohu a reset skóre.

### Lokální spuštění

V kořeni repozitáře spusť:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Otevři **http://127.0.0.1:8000/web/**. Neotvírej `index.html` přímo přes
`file://`: pro načtení JSON katalogu je potřeba HTTP server.

### Publikování na GitHub Pages

Po sloučení změn do `main` otevři **Settings → Pages → Build and deployment**:

1. Zvol **Deploy from a branch**.
2. Vyber větev **main**, složku **/(root)** a ulož nastavení.
3. Po dokončení nasazení otevři
   **https://milhouska-cen59600.github.io/sql-trainer-cli/web/**.

GitHub Pages při publikování z větve podporuje jen kořen nebo `/docs`,
nikoli přímý výběr `/web`. Proto publikujeme kořen a aplikaci otevíráme
na cestě `/web/`. Všechny odkazy na soubory aplikace jsou relativní.

### Vyhodnocování a skóre

- SQL se **neprovádí**. Porovnávají se tokeny bez ohledu na mezery a velikost
  písmen mimo textové literály; koncové středníky se ignorují. Textové literály
  musí odpovídat přesně. Významově ekvivalentní dotaz nemusí být přijat.
- Vysvětlení vyžaduje dvě očekávaná klíčová slova (nebo všechna, pokud je jen
  jedno). Textové kmeny se hledají jako podřetězce a čísla jako celé hodnoty.
  Bez klíčových slov se porovnává vzorová odpověď bez ohledu na velikost písmen.
- První neprázdná odpověď započítá pokus; správná přidá bod. Stejný pokus
  nelze skórovat dvakrát, ani po resetu skóre. Nová úloha znamená nový pokus.
- Nápověda body neovlivní. Stejně jako v Tkinter GUI po zobrazení řešení
  kontrola už nezmění skóre. Načtení další úlohy toto omezení zruší.
- Skóre se ukládá do `localStorage` daného prohlížeče a původu stránky.
  Při nedostupném úložišti aplikace funguje do obnovení stránky a zobrazí varování.
- Vyhodnocení je pouze klientské: odpovědi v katalogu jsou veřejné a skóre
  lze upravit v prohlížeči. Nejde o zabezpečený zkouškový systém.

### Katalog a testy webu

`web/tasks.json` je úplný export `TASKS` z `tasks.py`. Schéma zachovává pole
`id`, `difficulty`, `type`, `prompt`, `sql` (text nebo null), `hint`,
`solution`, `expected_answer` a `keywords` (pole textů). Při změně katalogu
export obnov z kořene repozitáře:

```sh
python -c "import json; from pathlib import Path; from tasks import TASKS; Path('web/tasks.json').write_text(json.dumps(TASKS, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')"
```

`python -m unittest test_web -v` ověří úplnost exportu a chování JavaScriptu
(kontrolu odpovědí, filtry, skórování, nápovědu/řešení a selhání úložiště/načítání).
JS testy používají pouze standardní Node.js; bez něj se přeskočí.
Celou původní i rozšířenou sadu spustí `python -m unittest discover -v`.
