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
## Live Demo
Frontend: https://fascinating-choux-642d36.netlify.app  
Backend: https://puzzleforge.onrender.com

