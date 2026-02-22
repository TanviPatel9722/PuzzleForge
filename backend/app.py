from __future__ import annotations

from fastapi import FastAPI, Response


from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
import json

from skyscrapers import Puzzle, Clues, generate_puzzle, solve_count_solutions, next_single_hint, reveal_best_clue

app = FastAPI(title="PuzzleForge (Skyscrapers Demo)", version="1.0")

@app.head("/")
def head_root():
    # Render health checks sometimes use HEAD /
    return Response(status_code=200)

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Static frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


class PuzzleIn(BaseModel):
    n: int = Field(..., ge=4, le=5)
    clues: Dict[str, List[int]]
    grid: List[List[int]]


@app.post("/api/verify")
def verify(puz: PuzzleIn):
    puzzle = Puzzle.from_dict(puz.model_dump())
    count, sol, stats = solve_count_solutions(puzzle, max_solutions=2)
    return {
        "has_solution": count > 0,
        "is_unique": count == 1,
        "solution_count_capped": count,
        "solution": sol,
        "stats": stats,
    }


@app.post("/api/hint")
def hint(puz: PuzzleIn):
    puzzle = Puzzle.from_dict(puz.model_dump())
    h = next_single_hint(puzzle)
    return {"hint": h}


@app.post("/api/reveal_clue")
def reveal_clue(puz: PuzzleIn):
    puzzle = Puzzle.from_dict(puz.model_dump())
    r = reveal_best_clue(puzzle)
    return {"reveal": r}


@app.get("/api/generate")
def generate(n: int = 4, difficulty: str = "easy", seed: Optional[int] = None):
    puzzle, solution = generate_puzzle(n=n, difficulty=difficulty, seed=seed)
    return {
        "puzzle": puzzle.to_dict(),
        "solution": solution,  # returned for local dev/demo; remove for production competition if desired
        "meta": {"difficulty": difficulty, "seed": seed},
    }
