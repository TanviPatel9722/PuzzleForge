// PuzzleForge — Verified Skyscrapers (Vanilla JS)

const $ = (id) => document.getElementById(id);

let currentPuzzle = null;
const MAX_REVEAL_HINTS = 3;
let revealHintsUsed = 0;

function setStatus(msg) {
  $("status").textContent = msg;
}

function setCertificate(obj) {
  const el = $("certificateBody");
  el.textContent = JSON.stringify(obj, null, 2);
}

function revealHintsLeft() {
  return Math.max(0, MAX_REVEAL_HINTS - revealHintsUsed);
}

function updateRevealHintUI() {
  const left = revealHintsLeft();
  const btn = $("revealBtn");
  btn.textContent = `Reveal 1 Cell (${left} left)`;
  btn.disabled = left <= 0;
}

function emptyGrid(n) {
  return Array.from({ length: n }, () => Array.from({ length: n }, () => 0));
}

function encodeShare(puzzleObj) {
  const json = JSON.stringify(puzzleObj);
  const b64 = btoa(unescape(encodeURIComponent(json)));
  return b64;
}

function decodeShare(b64) {
  const json = decodeURIComponent(escape(atob(b64)));
  return JSON.parse(json);
}

function getGridFromUI(n) {
  const grid = emptyGrid(n);
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const inp = document.querySelector(`input[data-r="${i}"][data-c="${j}"]`);
      const v = parseInt(inp.value, 10);
      grid[i][j] = Number.isFinite(v) ? v : 0;
    }
  }
  return grid;
}

function applyGridToUI(grid) {
  const n = grid.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      const inp = document.querySelector(`input[data-r="${i}"][data-c="${j}"]`);
      inp.value = grid[i][j] === 0 ? "" : String(grid[i][j]);
    }
  }
}

function validateUI() {
  if (!currentPuzzle) return;
  const n = currentPuzzle.n;
  const grid = getGridFromUI(n);

  // Clear states
  document.querySelectorAll(".cellInput").forEach(inp => {
    inp.classList.remove("bad");
    inp.classList.remove("good");
  });

  // Row dupes
  for (let i = 0; i < n; i++) {
    const seen = new Map();
    for (let j = 0; j < n; j++) {
      const v = grid[i][j];
      if (!v) continue;
      if (v < 1 || v > n) {
        markBad(i, j);
        continue;
      }
      if (seen.has(v)) {
        markBad(i, j);
        markBad(i, seen.get(v));
      } else {
        seen.set(v, j);
      }
    }
  }

  // Col dupes
  for (let j = 0; j < n; j++) {
    const seen = new Map();
    for (let i = 0; i < n; i++) {
      const v = grid[i][j];
      if (!v) continue;
      if (v < 1 || v > n) {
        markBad(i, j);
        continue;
      }
      if (seen.has(v)) {
        markBad(i, j);
        markBad(seen.get(v), j);
      } else {
        seen.set(v, i);
      }
    }
  }
}

function markBad(r, c) {
  const inp = document.querySelector(`input[data-r="${r}"][data-c="${c}"]`);
  if (inp) inp.classList.add("bad");
}

function markGood(r, c) {
  const inp = document.querySelector(`input[data-r="${r}"][data-c="${c}"]`);
  if (inp) inp.classList.add("good");
}

function renderPuzzle(puz) {
  currentPuzzle = puz;
  revealHintsUsed = 0;
  updateRevealHintUI();
  const n = puz.n;

  const host = $("puzzleHost");
  host.innerHTML = "";

  // Skyscrapers board is (n+2) x (n+2):
  // corners empty, top clues row, bottom clues row,
  // left and right clue columns.
  const tbl = document.createElement("table");
  tbl.className = "skys";

  for (let r = 0; r < n + 2; r++) {
    const tr = document.createElement("tr");
    for (let c = 0; c < n + 2; c++) {
      const td = document.createElement("td");

      const isCorner = (r === 0 || r === n + 1) && (c === 0 || c === n + 1);
      const isTopClue = (r === 0) && (c > 0 && c < n + 1);
      const isBottomClue = (r === n + 1) && (c > 0 && c < n + 1);
      const isLeftClue = (c === 0) && (r > 0 && r < n + 1);
      const isRightClue = (c === n + 1) && (r > 0 && r < n + 1);
      const isCell = (r > 0 && r < n + 1) && (c > 0 && c < n + 1);

      if (isCorner) {
        td.className = "clue";
        td.textContent = "";
      } else if (isTopClue) {
        td.className = "clue";
        td.dataset.side = "top";
        td.dataset.idx = String(c - 1);
        const v = puz.clues.top[c - 1];
        td.textContent = v ? String(v) : "";
      } else if (isBottomClue) {
        td.className = "clue";
        td.dataset.side = "bottom";
        td.dataset.idx = String(c - 1);
        const v = puz.clues.bottom[c - 1];
        td.textContent = v ? String(v) : "";
      } else if (isLeftClue) {
        td.className = "clue";
        td.dataset.side = "left";
        td.dataset.idx = String(r - 1);
        const v = puz.clues.left[r - 1];
        td.textContent = v ? String(v) : "";
      } else if (isRightClue) {
        td.className = "clue";
        td.dataset.side = "right";
        td.dataset.idx = String(r - 1);
        const v = puz.clues.right[r - 1];
        td.textContent = v ? String(v) : "";
      } else if (isCell) {
        td.className = "cell";
        const inp = document.createElement("input");
        inp.className = "cellInput";
        inp.inputMode = "numeric";
        inp.maxLength = 1;
        inp.dataset.r = String(r - 1);
        inp.dataset.c = String(c - 1);
        inp.addEventListener("input", () => {
          // keep only digits
          inp.value = inp.value.replace(/[^0-9]/g, "");
          validateUI();
        });
        td.appendChild(inp);
      }

      tr.appendChild(td);
    }
    tbl.appendChild(tr);
  }

  host.appendChild(tbl);
  validateUI();
  setCertificate("Not verified yet.");
  setStatus("Puzzle loaded. Fill the grid, then Verify for uniqueness.");
}

async function apiGenerate() {
  const n = parseInt($("sizeSelect").value, 10);
  const diff = $("diffSelect").value;
  const seedRaw = $("seedInput").value.trim();
  const seed = seedRaw.length ? parseInt(seedRaw, 10) : null;

  const url = new URL("/api/generate", window.location.origin);
  url.searchParams.set("n", String(n));
  url.searchParams.set("difficulty", diff);
  if (Number.isFinite(seed)) url.searchParams.set("seed", String(seed));

  setStatus("Generating…");
  const res = await fetch(url.toString());
  const data = await res.json();
  renderPuzzle(data.puzzle);

  // Optional: store in hash for persistence
  window.location.hash = encodeShare(data.puzzle);
  setStatus("Generated. (Saved into URL hash for sharing.)");
}

async function apiVerify() {
  if (!currentPuzzle) return;
  const n = currentPuzzle.n;
  const grid = getGridFromUI(n);
  const payload = { ...currentPuzzle, grid };

  setStatus("Verifying… (counting solutions up to 2)");
  const res = await fetch("/api/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  setCertificate({
    has_solution: data.has_solution,
    is_unique: data.is_unique,
    solution_count_capped: data.solution_count_capped,
    stats: data.stats,
  });

  if (!data.has_solution) {
    setStatus("No valid solution exists with your current entries. Undo some moves.");
  } else if (data.is_unique) {
    setStatus("✅ Unique solution verified (given your current entries).");
  } else {
    setStatus("⚠️ Multiple solutions possible (given your current entries). Keep solving / add constraints.");
  }
}

async function apiHint() {
  if (!currentPuzzle) return;
  const n = currentPuzzle.n;
  const grid = getGridFromUI(n);
  const payload = { ...currentPuzzle, grid };

  setStatus("Finding a single-step hint…");
  const res = await fetch("/api/hint", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();

  if (!data.hint) {
    setStatus("No single forced move found (or your grid is currently invalid). Try Verify or adjust entries.");
    return;
  }

  const { row, col, value } = data.hint;
  const inp = document.querySelector(`input[data-r="${row}"][data-c="${col}"]`);
  if (inp) {
    inp.value = String(value);
    markGood(row, col);
    validateUI();
  }
  setStatus(`Hint applied: r${row+1} c${col+1} = ${value}.`);
}

async function apiRevealClue() {
  if (!currentPuzzle) return;
  if (revealHintsLeft() <= 0) {
    setStatus("No reveal hints left. Maximum 3 per puzzle.");
    updateRevealHintUI();
    return;
  }

  const n = currentPuzzle.n;
  const grid = getGridFromUI(n);
  const payload = { ...currentPuzzle, grid };

  setStatus("Revealing one answer cell...");
  const res = await fetch("/api/reveal_clue", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  const r = data.reveal;

  if (!r) return setStatus("No cell could be revealed.");
  if (r.type === "invalid") return setStatus(`⚠️ ${r.message}`);
  if (r.type === "none") return setStatus(r.message || "No empty cells left.");

  const { row, col, value, reason, post_solution_count_capped } = r;
  const inp = document.querySelector(`input[data-r="${row}"][data-c="${col}"]`);
  if (inp) {
    inp.value = String(value);
    markGood(row, col);
    validateUI();
  }

  revealHintsUsed += 1;
  updateRevealHintUI();
  setStatus(`✅ Revealed r${row + 1} c${col + 1} = ${value}. ${reason} (solutions<=2 now: ${post_solution_count_capped}). Hints left: ${revealHintsLeft()}.`);
}

async function copyShareLink() {
  if (!currentPuzzle) return;
  const n = currentPuzzle.n;
  const grid = getGridFromUI(n);
  const payload = { ...currentPuzzle, grid };

  const hash = encodeShare(payload);
  const link = `${window.location.origin}/#${hash}`;

  try {
    await navigator.clipboard.writeText(link);
    setStatus("Share link copied to clipboard.");
  } catch {
    // fallback
    prompt("Copy this link:", link);
  }
}

function tryLoadFromHash() {
  const h = window.location.hash;
  if (!h || h.length < 2) return false;
  try {
    const b64 = h.slice(1);
    const obj = decodeShare(b64);
    renderPuzzle(obj);
    // apply grid if present
    if (obj.grid) applyGridToUI(obj.grid);
    setStatus("Loaded puzzle from shared link.");
    return true;
  } catch (e) {
    console.warn("Failed to load hash puzzle", e);
    return false;
  }
}

// Wire up
$("generateBtn").addEventListener("click", apiGenerate);
$("verifyBtn").addEventListener("click", apiVerify);
$("hintBtn").addEventListener("click", apiHint);
$("revealBtn").addEventListener("click", apiRevealClue);
$("shareBtn").addEventListener("click", copyShareLink);
updateRevealHintUI();

// Initialize
if (!tryLoadFromHash()) {
  // default generate medium
  apiGenerate();
}
