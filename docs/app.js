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
  const candidates = tasks.filter((task) =>
    task.difficulty === element("difficulty").value && task.type === element("task-type").value
  );
  const alternatives = candidates.filter((task) => task.id !== currentTask?.id);
  const pool = alternatives.length ? alternatives : candidates;
  currentTask = pool[Math.floor(Math.random() * pool.length)] || null;
  answered = false;
  solutionShown = false;
  element("feedback").textContent = "";
  element("answer").value = currentTask?.type === "find-bug" ? currentTask.sql || "" : "";
  element("prompt").textContent = currentTask?.prompt || "Pro tento výběr není dostupná úloha.";
  element("task-heading").textContent = currentTask ? `Zadání #${currentTask.id}` : "Zadání";
  element("sql-section").hidden = !currentTask?.sql;
  element("sql").textContent = currentTask?.sql || "";
  for (const name of ["hint", "solution"]) {
    element(`${name}-section`).hidden = true;
    element(name).textContent = "";
  }
  for (const name of ["answer", "check", "hint-button", "solution-button"]) {
    element(name).disabled = !currentTask;
  }
}

element("answer-form").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!currentTask || answered) return;
  const answer = element("answer").value;
  if (!answer.trim()) {
    element("feedback").textContent = "Nejprve napiš odpověď. Prázdná odpověď nespotřebuje pokus.";
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
  element("feedback").textContent = (correct ? "Správně!" : "Zatím ne. Prohlédni si vzorové řešení.") +
    (solutionShown ? " Řešení už bylo zobrazeno; skóre se nemění." :
      " Pokus byl započítán; další odpovědi skóre nezmění.");
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
  element("solution-section").hidden = false;
  element("feedback").textContent = "Řešení je zobrazeno. Další kontrola této úlohy už skóre nezmění.";
});

for (const name of ["load", "next", "difficulty", "task-type"]) {
  element(name).addEventListener(name === "difficulty" || name === "task-type" ? "change" : "click", loadTask);
}
element("reset").addEventListener("click", () => {
  score = { correct: 0, total: 0 };
  saveScore();
  element("feedback").textContent = "Skóre vynulováno. Nový pokus získáš načtením další úlohy.";
});

async function initialize() {
  loadScore();
  try {
    const response = await fetch("./tasks.json");
    if (!response.ok) throw new Error("Catalog request failed");
    const catalog = await response.json();
    if (!Array.isArray(catalog)) throw new Error("Invalid catalog");
    tasks = catalog;
    element("load").disabled = false;
    element("next").disabled = false;
    loadTask();
  } catch {
    element("prompt").textContent =
      "Katalog nelze načíst. Spusť web přes HTTP server (viz README), zkontroluj připojení a obnov stránku.";
  }
}

initialize();
