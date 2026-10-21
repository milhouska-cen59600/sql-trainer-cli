import json
from pathlib import Path
import shutil
import subprocess
import unittest

from tasks import TASKS


ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"


class WebCatalogTests(unittest.TestCase):
    def test_export_matches_complete_python_catalog(self):
        self.assertEqual(json.loads((WEB / "tasks.json").read_text(encoding="utf-8")), TASKS)

    def test_deployed_docs_match_web_app(self):
        for name in ("app.js", "index.html", "styles.css", "tasks.json"):
            with self.subTest(name=name):
                self.assertEqual((WEB / name).read_bytes(), (ROOT / "docs" / name).read_bytes())
        self.assertIn("[hidden] { display: none !important; }",
                      (WEB / "styles.css").read_text(encoding="utf-8"))
        self.assertNotIn(".innerHTML", (WEB / "app.js").read_text(encoding="utf-8"))


@unittest.skipUnless(shutil.which("node"), "Node.js is needed for JavaScript regression tests")
class WebBehaviorTests(unittest.TestCase):
    def run_js(self, assertions, *, storage="null", fail_fetch=False, blocked_storage=False):
        harness = r"""
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const elements = new Map();
function makeElement() {
  return {
    value: "", _textContent: "", children: [], hidden: true, disabled: false, listeners: {},
    get textContent() {
      return this.children.length ? this.children.map((child) => child.textContent).join("") : this._textContent;
    },
    set textContent(value) { this._textContent = String(value); this.children = []; },
    appendChild(child) { this.children.push(child); return child; },
    replaceChildren(...children) { this.children = children; this._textContent = ""; },
    addEventListener(name, callback) { this.listeners[name] = callback; }
  };
}
const document = { getElementById(id) {
  if (!elements.has(id)) elements.set(id, makeElement());
  return elements.get(id);
}, createElement: makeElement, createTextNode(text) { return { textContent: text }; }};
document.getElementById("difficulty").value = "beginner";
document.getElementById("task-type").value = "write-query";
let stored = STORAGE;
const context = vm.createContext({
  assert, document,
  catalog: JSON.parse(fs.readFileSync("web/tasks.json", "utf8")),
  localStorage: {
    getItem() { if (BLOCKED) throw Error("blocked"); return stored; },
    setItem(key, value) { if (BLOCKED) throw Error("blocked"); stored = value; }
  },
  fetch: async () => {
    if (FAIL_FETCH) throw Error("offline");
    return { ok: true, json: async () => JSON.parse(fs.readFileSync("web/tasks.json", "utf8")) };
  }
});
vm.runInContext(fs.readFileSync("web/app.js", "utf8"), context);
setImmediate(() => {
  vm.runInContext(`
    const click = (id) => element(id).listeners.click();
    const submit = (answer) => {
      element("answer").value = answer;
      element("answer-form").listeners.submit({ preventDefault() {} });
    };
    ASSERTIONS
  `, context);
});
"""
        harness = harness.replace("STORAGE", json.dumps(storage))
        harness = harness.replace("BLOCKED", str(blocked_storage).lower())
        harness = harness.replace("FAIL_FETCH", str(fail_fetch).lower())
        harness = harness.replace("ASSERTIONS", assertions)
        result = subprocess.run(
            ["node", "-e", harness], cwd=ROOT, capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_idle_start_pending_selection_and_next(self):
        self.run_js("""
          assert.equal(currentTask, null);
          assert.ok(element("load").disabled === false);
          assert.ok(element("next").disabled);
          assert.ok(element("answer").disabled);
          assert.ok(element("check").disabled);
          assert.ok(element("hint-button").disabled);
          assert.ok(element("solution-button").disabled);
          assert.ok(element("format-button").hidden);
          assert.ok(element("prompt").textContent.includes("klikni na Spustit"));
          element("difficulty").value = "intermediate";
          element("difficulty").listeners.change();
          assert.equal(currentTask, null);
          assert.ok(element("next").disabled);
          click("next");
          assert.equal(currentTask, null);
          click("load");
          assert.ok(currentTask);
          assert.equal(currentTask.difficulty, "intermediate");
          const startedId = currentTask.id;
          element("task-type").value = "find-bug";
          element("task-type").listeners.change();
          assert.equal(currentTask, null);
          assert.equal(element("answer").disabled, true, "answer stays disabled for a pending selection");
          assert.ok(element("next").disabled);
          submit("should not score");
          assert.equal(score.total, 0);
          assert.ok(element("prompt").textContent.includes("až po kliknutí na Spustit"));
          click("load");
          assert.equal(currentTask.difficulty, "intermediate");
          assert.equal(currentTask.type, "find-bug");
          assert.ok(currentTask.id !== startedId);
          const nextId = currentTask.id;
          click("next");
          assert.ok(currentTask);
          assert.notEqual(currentTask.id, nextId);
        """)

    def test_all_catalog_answers_and_filter_combinations(self):
        self.run_js("""
          assert.equal(currentTask, null);
          for (const task of catalog) {
            assert.ok(checkAnswer(task.expected_answer, task), task.id);
            assert.ok(!checkAnswer("nesprávná odpověď", task), task.id);
            element("difficulty").value = task.difficulty;
            element("task-type").value = task.type;
            element("difficulty").listeners.change();
            assert.equal(currentTask, null);
            loadTask();
            assert.equal(currentTask.difficulty, task.difficulty);
            assert.equal(currentTask.type, task.type);
            assert.equal(element("sql-section").hidden, !currentTask.sql);
            assert.equal(element("format-button").hidden, task.type === "explain-result");
            if (task.type === "find-bug") {
              assert.deepEqual(normalizeSql(element("answer").value), normalizeSql(currentTask.sql));
              assert.ok(!checkAnswer(task.sql, task));
            }
          }
        """)

    def test_sql_formatting_preserves_literals_comments_identifiers_and_tokens(self):
        self.run_js("""
          const quote = String.fromCharCode(34);
          const source = "select " + quote + "order by" + quote +
            ", q'[FROM -- untouched]' as note" +
            String.fromCharCode(10) + "from accounts /* WHERE remains a comment */" +
            String.fromCharCode(10) + "where note = 'Order BY -- text' -- GROUP BY ignored" +
            String.fromCharCode(10) + "order by account_id";
          const formatted = formatSql(source);
          const tokens = (sql) => tokenizeSql(sql)
            .filter((token) => token.type !== "whitespace")
            .map((token) => token.type + ":" + token.text);
          assert.deepEqual(tokens(formatted), tokens(source));
          assert.ok(formatted.includes("q'[FROM -- untouched]'"));
          assert.ok(formatted.includes("'Order BY -- text'"));
          assert.ok(formatted.includes("/* WHERE remains a comment */"));
          assert.ok(formatted.includes("-- GROUP BY ignored"));
          assert.ok(formatted.includes('"order by"'));
          const newline = String.fromCharCode(10);
          assert.ok(formatted.includes(newline + "from accounts"));
          assert.ok(formatted.includes(newline + "where"));
          assert.ok(formatted.includes(newline + "order by"));
          const analytic = formatSql(
            "SELECT ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at) FROM accounts"
          );
          assert.ok(analytic.includes("OVER (" + newline));
          assert.ok(analytic.includes(newline + "  PARTITION BY"), analytic);
          assert.ok(analytic.includes(newline + "  ORDER BY"), analytic);
          for (const task of catalog.filter((item) => item.type !== "explain-result")) {
            for (const sql of [task.sql, task.solution, task.expected_answer].filter(Boolean)) {
              assert.deepEqual(tokens(formatSql(sql)), tokens(sql), task.id + ": " + sql);
            }
          }
          assert.ok(checkAnswer("SELECT name FROM customers WHERE city='New York'",
            { type: "write-query", expected_answer: "select name from customers where city = 'New York'" }));
          assert.equal(element("solution").textContent, "");
          tasks = [{
            id: 999, difficulty: "beginner", type: "write-query", prompt: "Format",
            solution: "SELECT name FROM customers", expected_answer: "SELECT name FROM customers"
          }];
          element("difficulty").value = "beginner";
          element("task-type").value = "write-query";
          loadTask();
          assert.ok(!element("format-button").hidden);
          element("answer").value = "select name from customers";
          click("format-button");
          assert.ok(checkAnswer(element("answer").value, currentTask));
          click("solution-button");
          assert.equal(element("solution").textContent, formatSql(currentTask.solution));
          assert.ok(element("solution").children.some((child) => child.className === "sql-keyword"));
        """)

    def test_sql_normalization_and_keyword_boundaries(self):
        self.run_js("""
          const sql = { type: "write-query", expected_answer: "SELECT name FROM customers WHERE city = 'New York'" };
          assert.ok(checkAnswer(" select NAME from customers where city='New York';; ", sql));
          assert.ok(!checkAnswer("SELECT name FROM customers WHERE city='new york'", sql));
          assert.ok(!checkAnswer("SELECT name FROM customers WHERE city='New  York'", sql));
          const explanation = { type: "explain-result", keywords: ["součet", "150", "1500"] };
          assert.ok(!checkAnswer("1500", explanation));
          assert.ok(checkAnswer("Součet je 1500", explanation));
          for (const number of ["11500", "-1500", "1500.5", "1500,5", "x1500"]) {
            assert.ok(!checkAnswer("součet " + number, explanation), number);
          }
        """)

    def test_scoring_hint_solution_next_and_reset(self):
        self.run_js("""
          assert.equal(currentTask, null);
          click("load");
          submit("  ");
          assert.equal(score.total, 0);
          assert.ok(!answered);
          element("answer").value = "rozepsaná odpověď";
          click("hint-button");
          assert.equal(element("answer").value, "rozepsaná odpověď");
          assert.ok(!element("hint-section").hidden);
          submit(currentTask.expected_answer);
          assert.equal(score.correct, 1);
          assert.equal(score.total, 1);
          submit(currentTask.expected_answer);
          assert.equal(score.total, 1);
          click("reset");
          submit(currentTask.expected_answer);
          assert.equal(score.total, 0);
          const previous = currentTask.id;
          click("next");
          assert.notEqual(currentTask.id, previous);
          assert.ok(element("hint-section").hidden);
          submit("wrong");
          submit(currentTask.expected_answer);
          assert.equal(score.correct, 0);
          assert.equal(score.total, 1);
          click("next");
          click("solution-button");
          assert.ok(!element("solution-section").hidden);
          submit(currentTask.expected_answer);
          assert.equal(score.total, 1);
          click("next");
          submit(currentTask.expected_answer);
          assert.equal(score.correct, 1);
          assert.equal(score.total, 2);
          assert.equal(JSON.parse(localStorage.getItem(SCORE_KEY)).correct, 1);
        """)

    def test_persistence_and_invalid_saved_score(self):
        self.run_js("assert.equal(element('score').textContent, 'Skóre: 2/3');",
                    storage='{"correct":2,"total":3}')
        for saved in ('{"correct":5,"total":1}', '{"correct":-1,"total":2}', "broken"):
            self.run_js("assert.equal(score.total, 0);", storage=saved)

    def test_storage_and_fetch_failure(self):
        self.run_js("""
          assert.equal(currentTask, null);
          click("load");
          assert.ok(currentTask);
          submit(currentTask.expected_answer);
          assert.equal(score.correct, 1);
          assert.ok(!element("storage-warning").hidden);
        """, blocked_storage=True)
        self.run_js("""
          assert.equal(currentTask, null);
          assert.ok(element("next").disabled);
          assert.ok(element("prompt").textContent.includes("HTTP"));
        """, fail_fetch=True)

    def test_missing_optional_fields_and_empty_selection(self):
        self.run_js("""
          tasks = [{ id: 100, difficulty: "beginner", type: "write-query", prompt: "Test" }];
          loadTask();
          click("hint-button");
          click("solution-button");
          assert.ok(element("hint").textContent.includes("není"));
          assert.ok(element("solution").textContent.includes("není"), element("solution").textContent);
          assert.ok(element("sql-section").hidden);
          assert.ok(checkAnswer("výsledek", {type: "explain-result", solution: "Výsledek"}));
          element("difficulty").value = "unknown";
          loadTask();
          assert.equal(currentTask, null);
          assert.ok(element("check").disabled);
          assert.ok(element("answer").disabled);
        """)


if __name__ == "__main__":
    unittest.main()
