<<<<<<< HEAD
# PuzzleForge
=======
# PuzzleForge — Verified Skyscrapers (Hackathon-ready Demo)

This is a **puzzle-themed application** that:
- Generates Skyscrapers puzzles (4×4 or 5×5) deterministically (seeded)
- Verifies whether the puzzle (given current user entries) has a solution and whether it is **unique**
- Offers a “single forced move” **Hint**
- Creates a **shareable link** (URL hash) that includes the puzzle + your current progress

It’s built to score well on:
- Representation (puzzle game)
- Innovation (generation + verification)
- Completeness (polished UX)
- Presentation (demo-friendly flow)
- Wow Point (uniqueness certificate / proof-of-solve)

---

## Quickstart

### 1) Create a virtual environment & install deps
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2) Run the server
```bash
uvicorn app:app --reload --port 8000
```

Open:
- http://127.0.0.1:8000

---

## API Endpoints

- `GET /api/generate?n=4&difficulty=easy|medium|hard&seed=42`
- `POST /api/verify`  (counts solutions up to 2 and returns certificate info)
- `POST /api/hint`    (returns a “single forced move” if available)

---

## Notes for your hackathon submission

- For competition submission, you may want to remove the `solution` field from `/api/generate`
  (it’s returned now only for local testing).
- The solver is a deterministic backtracker optimized for 4×4 and 5×5. This keeps the project
  fast, reliable, and demo-friendly.

---

## License
MIT (you can replace as needed).
>>>>>>> 8388f3b (Initial commit: PuzzleForge)
