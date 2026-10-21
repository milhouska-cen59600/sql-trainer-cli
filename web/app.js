"use strict";

// tasks.json is the complete tasks.TASKS array, preserving Python field names:
// id, difficulty (beginner/intermediate/advanced), type, prompt, sql (nullable),
// hint, solution, expected_answer, keywords (array; used for explain-result).
// Junior/Medior/Senior are UI labels only. Optional display fields may be absent.
const SCORE_KEY = "sql-trainer.score.v1";
const element = (id) => document.getElementById(id);
let tasks = [];
let currentTask = null;
let answered = false;
let solutionShown = false;
let score = { correct: 0, total: 0 };
let catalogReady = false;
let hasStarted = false;
let pendingSelection = false;

function tokenizeSql(text) {
  const tokens = [];
  let index = 0;
  while (index < text.length) {
    const rest = text.slice(index);
    let match;
    let type;
    if ((match = rest.match(/^\s+/))) {
      type = "whitespace";
    } else if ((match = rest.match(/^--[^\r\n]*/))) {
      type = "comment";
    } else if ((match = rest.match(/^\/\*[\s\S]*?\*\//))) {
      type = "comment";
    } else if ((match = rest.match(/^(?:[nN])?[qQ]'/))) {
      const delimiter = rest[match[0].length];
      const closing = ({ "[": "]", "(": ")", "{": "}", "<": ">" })[delimiter] || delimiter;
      const end = rest.indexOf(`${closing}'`, match[0].length + 1);
      match = [end < 0 ? rest : rest.slice(0, end + 2)];
      type = "string";
    } else if ((match = rest.match(/^(?:[nN])?'(?:''|[^'])*'/))) {
      type = "string";
    } else if ((match = rest.match(/^"(?:\"\"|[^"])*"/))) {
      type = "identifier";
    } else if ((match = rest.match(/^[\p{L}_][\p{L}\p{N}_$#]*/u))) {
      type = "word";
    } else if ((match = rest.match(/^\d+(?:\.\d+)?/))) {
      type = "number";
    } else {
      match = [text[index]];
      type = "symbol";
    }
    tokens.push({ text: match[0], type });
    index += match[0].length;
  }
  return tokens;
}

function formatSql(text) {
  const tokens = tokenizeSql(text).filter((token) => token.type !== "whitespace");
  const output = [];
  const analytic = [];
  let depth = 0;
  let indent = 0;
  let position = 0;
  const trimLine = () => {
    while (output.length && /^ *$/.test(output[output.length - 1])) output.pop();
  };
  const newLine = (spaces) => {
    trimLine();
    while (output.length && output[output.length - 1] === "\n") output.pop();
    if (output.length) output.push("\n");
    if (spaces) output.push(" ".repeat(spaces));
  };
  const write = (value, forceSpace = false) => {
    const previous = output[output.length - 1] || "";
    const atLineIndent = output.length > 1 && output[output.length - 2] === "\n" &&
      /^ *$/.test(previous);
    const first = value[0];
    const functionParen = value === "(" &&
      /^[\p{L}_][\p{L}\p{N}_$#]*$/u.test(previous) &&
      !/^(SELECT|FROM|WHERE|IN|EXISTS|OVER|AS|CASE|WHEN|THEN|ELSE|END|BY|AND|OR|NOT|ON|JOIN|GROUP|ORDER|HAVING)$/i.test(previous);
    const tightBefore = /^[),.;]/.test(value) || value === "." || value === "::" || functionParen;
    const tightAfterPrevious = previous === "(" || previous === "." || previous === "::";
    if (forceSpace && previous && previous !== "\n" && !atLineIndent && !previous.endsWith(" ")) output.push(" ");
    else if (!forceSpace && previous && previous !== "\n" && !atLineIndent && !previous.endsWith(" ") &&
        !tightBefore && !tightAfterPrevious && first !== "\n") output.push(" ");
    output.push(value);
  };
  const phraseAt = (index) => {
    if (tokens[index]?.type !== "word" || tokens[index + 1]?.type !== "word") return "";
    const phrase = `${tokens[index].text} ${tokens[index + 1].text}`;
    return ["GROUP BY", "ORDER BY", "PARTITION BY", "CONNECT BY", "START WITH", "UNION ALL"].includes(phrase.toUpperCase())
      ? phrase
      : "";
  };
  const lineAt = (spaces) => {
    newLine(spaces);
    indent = spaces;
  };

  while (position < tokens.length) {
    const token = tokens[position];
    const upper = token.type === "word" ? token.text.toUpperCase() : "";
    const phrase = phraseAt(position);
    if (token.type === "comment") {
      if (output.length && output[output.length - 1] !== "\n") write(" ", true);
      write(token.text);
      lineAt(analytic.length ? indent : 0);
      position += 1;
      continue;
    }
    if (phrase) {
      const isAnalyticClause = analytic.length > 0 &&
        (phrase.toUpperCase() === "PARTITION BY" || phrase.toUpperCase() === "ORDER BY");
      lineAt(isAnalyticClause ? 2 : 0);
      write(phrase);
      indent = 2;
      newLine(indent);
      position += 2;
      continue;
    }
    if (upper === "SELECT") {
      lineAt(analytic.length ? 2 : 0);
      write(token.text);
      indent = 2;
      newLine(indent);
      position += 1;
      continue;
    }
    if (upper === "FROM" || upper === "WHERE" || upper === "HAVING" ||
        upper === "UNION" || upper === "JOIN" || upper === "ON" ||
        upper === "AND" || upper === "OR") {
      const isJoinPrefix = ["LEFT", "RIGHT", "FULL", "INNER", "CROSS", "NATURAL"].includes(upper) &&
        tokens[position + 1]?.text.toUpperCase() === "JOIN";
      if (isJoinPrefix) {
        lineAt(0);
        write(`${token.text} ${tokens[position + 1].text}`);
        indent = 2;
        position += 2;
        continue;
      }
      const isCondition = upper === "AND" || upper === "OR";
      const isOn = upper === "ON";
      lineAt(isCondition ? (analytic.length ? 4 : 2) : (isOn ? 2 : 0));
      write(token.text);
      indent = isCondition ? (analytic.length ? 4 : 2) : (isOn ? 4 : 2);
      if (upper !== "FROM" && upper !== "JOIN") newLine(indent);
      position += 1;
      continue;
    }
    if (upper === "OVER" && tokens[position + 1]?.text === "(") {
      write(token.text);
      write("(");
      depth += 1;
      analytic.push({ closeAt: depth });
      indent = 2;
      newLine(indent);
      position += 2;
      continue;
    }
    if (token.text === "(") {
      write(token.text);
      depth += 1;
      position += 1;
      continue;
    }
    if (token.text === ")") {
      if (analytic.length && analytic[analytic.length - 1].closeAt === depth) {
        lineAt(2);
        analytic.pop();
      }
      write(token.text);
      depth = Math.max(0, depth - 1);
      position += 1;
      continue;
    }
    if (token.text === "," && depth === 0) {
      write(token.text);
      newLine(indent || 2);
      position += 1;
      continue;
    }
    if (token.text === ";") {
      write(token.text);
      position += 1;
      continue;
    }
    write(token.text);
    position += 1;
  }
  return output.join("").trim();
}

function renderSql(container, text) {
  container.replaceChildren();
  for (const token of tokenizeSql(formatSql(text))) {
    if (token.type === "whitespace") {
      container.appendChild(document.createTextNode(token.text));
      continue;
    }
    const span = document.createElement("span");
    span.className = token.type === "word" &&
      /^(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|FULL|INNER|CROSS|ON|AND|OR|GROUP|BY|ORDER|HAVING|AS|IN|IS|NULL|NOT|EXISTS|CASE|WHEN|THEN|ELSE|END|OVER|PARTITION|UNION|ALL|DISTINCT|WITH|CONNECT|START|FETCH|OFFSET|ROWS|RANGE|BETWEEN|CURRENT|ROW|ASC|DESC)$/i.test(token.text)
      ? "sql-keyword"
      : `sql-${token.type}`;
    span.textContent = token.text;
    container.appendChild(span);
  }
}

function setFeedback(message, kind = "") {
  element("feedback").textContent = message;
  element("feedback").className = kind ? `feedback ${kind}` : "feedback";
}

function disableTaskActions() {
  for (const name of ["answer", "check", "hint-button", "solution-button", "format-button"]) {
    element(name).disabled = true;
  }
  element("format-button").hidden = true;
}

function normalizeSql(text) {
  const tokens = text.trim().match(
    /'(?:''|[^'])*'|[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|>=|<=|<>|!=|[^\s]/g
  ) || [];
  while (tokens[tokens.length - 1] === ";") tokens.pop();
  return tokens.map((token) => token.startsWith("'") ? token : token.toLowerCase());
}

function checkAnswer(answer, task) {
  const expected = task.expected_answer || task.solution || "";
  if (task.type === "write-query" || task.type === "find-bug") {
    return Boolean(expected) &&
      JSON.stringify(normalizeSql(answer)) === JSON.stringify(normalizeSql(expected));
  }
  if (task.type !== "explain-result") return false;
  const keywords = Array.isArray(task.keywords) ? task.keywords : [];
  if (!keywords.length) {
    return Boolean(expected) && answer.trim().toLowerCase() === expected.trim().toLowerCase();
  }
  const text = answer.toLowerCase();
  // Match complete signed/decimal numbers, not overlapping numeric substrings.
  const numbers = new Set(text.match(
    /(?<![\p{L}\p{N}_.+-])[+-]?\d+(?:[.,]\d+)?(?![\p{L}\p{N}_]|[.,]\d)/gu
  ) || []);
  const matches = keywords.filter((keyword) => {
    const word = String(keyword).toLowerCase();
    return /^[+-]?\d+(?:[.,]\d+)?$/.test(word) ? numbers.has(word) : text.includes(word);
  }).length;
  return matches >= Math.min(2, keywords.length);
}

function storageWarning() {
  element("storage-warning").hidden = false;
  element("storage-warning").textContent =
    "Skóre nelze uložit do prohlížeče; zůstane pouze do obnovení stránky.";
}

function renderScore() {
  element("score").textContent = `Skóre: ${score.correct}/${score.total}`;
}

function saveScore() {
  renderScore();
  try {
    localStorage.setItem(SCORE_KEY, JSON.stringify(score));
  } catch {
    storageWarning();
  }
}

function loadScore() {
  try {
    const saved = JSON.parse(localStorage.getItem(SCORE_KEY));
    if (saved && Number.isSafeInteger(saved.correct) && Number.isSafeInteger(saved.total) &&
        saved.correct >= 0 && saved.total >= saved.correct) {
      score = { correct: saved.correct, total: saved.total };
    }
  } catch {
    storageWarning();
  }
  renderScore();
}

function loadTask() {
  if (!catalogReady) return;
  const candidates = tasks.filter((task) =>
    task.difficulty === element("difficulty").value && task.type === element("task-type").value
  );
  const alternatives = candidates.filter((task) => task.id !== currentTask?.id);
  const pool = alternatives.length ? alternatives : candidates;
  currentTask = pool[Math.floor(Math.random() * pool.length)] || null;
  hasStarted = true;
  pendingSelection = false;
  answered = false;
  solutionShown = false;
  setFeedback("");
  element("answer").value = currentTask?.type === "find-bug" ? formatSql(currentTask.sql || "") : "";
  element("prompt").textContent = currentTask?.prompt ||
    "Pro tento výběr není dostupná úloha. Změň výběr a klikni na Spustit.";
  element("task-heading").textContent = currentTask ? `Zadání #${currentTask.id}` : "Zadání";
  element("sql-section").hidden = !currentTask?.sql;
  if (currentTask?.sql) renderSql(element("sql"), currentTask.sql);
  else element("sql").replaceChildren();
  for (const name of ["hint", "solution"]) {
    element(`${name}-section`).hidden = true;
    element(name).textContent = "";
  }
  element("load").textContent = "Spustit znovu";
  element("selection-note").textContent = "Nastavení použito. Další úlohu můžeš načíst tlačítkem Další úloha.";
  element("next").disabled = false;
  element("answer").disabled = !currentTask;
  element("check").disabled = !currentTask;
  element("hint-button").disabled = !currentTask;
  element("solution-button").disabled = !currentTask;
  element("format-button").hidden = !currentTask || currentTask.type === "explain-result";
  element("format-button").disabled = !currentTask;
}

function deferSelection() {
  if (!catalogReady) return;
  pendingSelection = true;
  if (hasStarted) {
    currentTask = null;
    answered = false;
    solutionShown = false;
    element("task-heading").textContent = "Zadání";
    element("sql-section").hidden = true;
    element("answer").value = "";
    element("prompt").textContent =
      "Nastavení bylo změněno. Nový výběr se použije až po kliknutí na Spustit.";
    element("selection-note").textContent = "Změny nastavení čekají na potvrzení tlačítkem Spustit.";
    for (const name of ["hint-section", "solution-section"]) element(name).hidden = true;
    disableTaskActions();
    element("next").disabled = true;
  } else {
    element("prompt").textContent =
      "Výběr je připraven. Klikni na Spustit, až budeš chtít načíst úlohu.";
    element("selection-note").textContent = "Úloha se načte až po kliknutí na Spustit.";
  }
  setFeedback("Změny nastavení se použijí až po kliknutí na Spustit.", "pending");
}

element("answer-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!currentTask || answered) return;
  const answer = element("answer").value;
  if (!answer.trim()) {
    setFeedback("Nejprve napiš odpověď. Prázdná odpověď nespotřebuje pokus.", "error");
    return;
  }
  answered = true;
  const correct = checkAnswer(answer, currentTask);
  if (!solutionShown) {
    score.total += 1;
    if (correct) score.correct += 1;
    saveScore();
  }
  element("check").disabled = true;
  setFeedback((correct ? "Správně!" : "Zatím ne. Prohlédni si vzorové řešení.") +
    (solutionShown ? " Řešení už bylo zobrazeno; skóre se nemění." :
      " Pokus byl započítán; další odpovědi skóre nezmění."), correct ? "success" : "error");
});

element("hint-button").addEventListener("click", () => {
  if (!currentTask) return;
  element("hint").textContent = currentTask.hint || "K této úloze není nápověda.";
  element("hint-section").hidden = false;
});

element("solution-button").addEventListener("click", () => {
  if (!currentTask) return;
  solutionShown = true;
  element("solution").textContent =
    currentTask.solution || currentTask.expected_answer || "Řešení není dostupné.";
  if (currentTask.type !== "explain-result") {
    renderSql(element("solution"), currentTask.solution || currentTask.expected_answer || "Řešení není dostupné.");
  }
  element("solution-section").hidden = false;
  setFeedback("Řešení je zobrazeno. Další kontrola této úlohy už skóre nezmění.", "pending");
});

element("load").addEventListener("click", loadTask);
element("next").addEventListener("click", () => {
  if (hasStarted && !pendingSelection) loadTask();
});
for (const name of ["difficulty", "task-type"]) {
  element(name).addEventListener("change", deferSelection);
}
element("format-button").addEventListener("click", () => {
  if (currentTask && currentTask.type !== "explain-result") {
    element("answer").value = formatSql(element("answer").value);
  }
});
element("reset").addEventListener("click", () => {
  score = { correct: 0, total: 0 };
  saveScore();
  setFeedback("Skóre vynulováno. Nový pokus získáš načtením další úlohy.", "pending");
});

async function initialize() {
  loadScore();
  disableTaskActions();
  try {
    const response = await fetch("./tasks.json");
    if (!response.ok) throw new Error("Catalog request failed");
    const catalog = await response.json();
    if (!Array.isArray(catalog)) throw new Error("Invalid catalog");
    tasks = catalog;
    catalogReady = true;
    element("load").disabled = false;
    element("next").disabled = true;
    element("prompt").textContent =
      "Vyber obtížnost a typ úlohy, potom klikni na Spustit. Úloha se nenačte, dokud ji sám nespustíš.";
  } catch {
    catalogReady = false;
    disableTaskActions();
    element("load").disabled = true;
    element("next").disabled = true;
    element("prompt").textContent =
      "Katalog nelze načíst. Spusť web přes HTTP server (viz README), zkontroluj připojení a obnov stránku.";
  }
}

initialize();
