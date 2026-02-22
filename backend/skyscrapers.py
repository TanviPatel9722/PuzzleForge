from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Iterable
import itertools
import random
import time

Grid = List[List[int]]  # 0 = empty


def visible_count(seq: List[int]) -> int:
    """Count visible skyscrapers scanning from left to right."""
    m = 0
    c = 0
    for x in seq:
        if x > m:
            m = x
            c += 1
    return c


@dataclass(frozen=True)
class Clues:
    top: List[int]
    bottom: List[int]
    left: List[int]
    right: List[int]

    def size(self) -> int:
        return len(self.top)


@dataclass
class Puzzle:
    n: int
    clues: Clues
    grid: Grid  # optional givens (typically all 0)

    def to_dict(self) -> Dict:
        return {
            "n": self.n,
            "clues": {
                "top": self.clues.top,
                "bottom": self.clues.bottom,
                "left": self.clues.left,
                "right": self.clues.right,
            },
            "grid": self.grid,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Puzzle":
        n = int(d["n"])
        c = d["clues"]
        clues = Clues(
            top=list(map(int, c["top"])),
            bottom=list(map(int, c["bottom"])),
            left=list(map(int, c["left"])),
            right=list(map(int, c["right"])),
        )
        grid = [list(map(int, row)) for row in d.get("grid", [[0]*n for _ in range(n)])]
        return Puzzle(n=n, clues=clues, grid=grid)


def _all_row_perms(n: int) -> List[Tuple[int, ...]]:
    return list(itertools.permutations(range(1, n + 1)))


def _row_ok_with_givens(row_perm: Tuple[int, ...], givens: List[int]) -> bool:
    for j, g in enumerate(givens):
        if g != 0 and row_perm[j] != g:
            return False
    return True


def _filter_rows_by_clues(perms: List[Tuple[int, ...]], left: int, right: int) -> List[Tuple[int, ...]]:
    out = []
    for p in perms:
        if left and visible_count(list(p)) != left:
            continue
        if right and visible_count(list(reversed(p))) != right:
            continue
        out.append(p)
    return out


def _col_visibility(col: List[int]) -> Tuple[int, int]:
    return visible_count(col), visible_count(list(reversed(col)))


def solve_count_solutions(puzzle: Puzzle, max_solutions: int = 2) -> Tuple[int, Optional[Grid], Dict]:
    """
    Count solutions up to max_solutions.
    Returns: (count, one_solution_grid_or_None, stats)
    """
    n = puzzle.n
    clues = puzzle.clues
    givens = puzzle.grid

    perms = _all_row_perms(n)

    # Candidate rows per row index given left/right and givens.
    row_candidates: List[List[Tuple[int, ...]]] = []
    for i in range(n):
        cands = _filter_rows_by_clues(perms, clues.left[i], clues.right[i])
        cands = [p for p in cands if _row_ok_with_givens(p, givens[i])]
        row_candidates.append(cands)

    # Order rows by branching factor (MRV)
    order = sorted(range(n), key=lambda i: len(row_candidates[i]))
    inv_order = {ri: k for k, ri in enumerate(order)}

    # Prepare structures
    col_used = [set() for _ in range(n)]
    grid: List[List[int]] = [[0]*n for _ in range(n)]

    nodes = 0
    solutions: List[Grid] = []

    def col_partial_ok(j: int, upto_rows: int) -> bool:
        """
        Very lightweight pruning for top/bottom clues based on partial column.
        We only ensure we haven't already exceeded the top clue visibility, and
        that it's still possible to reach it.
        """
        top = clues.top[j]
        bottom = clues.bottom[j]
        col_vals = [grid[r][j] for r in range(n) if grid[r][j] != 0]

        # If complete, check exact.
        if upto_rows == n:
            full_col = [grid[r][j] for r in range(n)]
            t, b = _col_visibility(full_col)
            if top and t != top:
                return False
            if bottom and b != bottom:
                return False
            return True

        # Partial checks only for top (from row 0 downward) and bottom (from row n-1 upward)
        # Since we fill rows in reordered order, partial can be messy; keep this conservative.
        # We'll just do a cheap feasibility check when column is fully assigned.
        return True

    def backtrack(k: int):
        nonlocal nodes
        if len(solutions) >= max_solutions:
            return
        nodes += 1
        if k == n:
            # verify columns clues & givens already applied
            for j in range(n):
                full_col = [grid[r][j] for r in range(n)]
                t, b = _col_visibility(full_col)
                if clues.top[j] and t != clues.top[j]:
                    return
                if clues.bottom[j] and b != clues.bottom[j]:
                    return
            solutions.append([row[:] for row in grid])
            return

        i = order[k]  # actual row index in original grid
        for row_perm in row_candidates[i]:
            # Check column uniqueness compatibility
            ok = True
            for j, val in enumerate(row_perm):
                if val in col_used[j]:
                    ok = False
                    break
            if not ok:
                continue

            # Place
            for j, val in enumerate(row_perm):
                grid[i][j] = val
                col_used[j].add(val)

            # If any columns completed, enforce top/bottom
            for j in range(n):
                # column complete if all rows filled
                if all(grid[r][j] != 0 for r in range(n)):
                    if not col_partial_ok(j, n):
                        ok = False
                        break

            if ok:
                backtrack(k + 1)

            # Unplace
            for j, val in enumerate(row_perm):
                col_used[j].remove(val)
                grid[i][j] = 0

            if len(solutions) >= max_solutions:
                return

    t0 = time.perf_counter()
    backtrack(0)
    t1 = time.perf_counter()

    sol = solutions[0] if solutions else None
    stats = {
        "nodes": nodes,
        "time_ms": round((t1 - t0) * 1000, 2),
        "max_solutions_cap": max_solutions,
    }
    return len(solutions), sol, stats


def has_any_solution(puzzle: Puzzle) -> bool:
    c, _, _ = solve_count_solutions(puzzle, max_solutions=1)
    return c > 0


def compute_full_clues(solution: Grid) -> Clues:
    n = len(solution)
    top = []
    bottom = []
    left = []
    right = []
    for j in range(n):
        col = [solution[i][j] for i in range(n)]
        top.append(visible_count(col))
        bottom.append(visible_count(list(reversed(col))))
    for i in range(n):
        row = solution[i]
        left.append(visible_count(row))
        right.append(visible_count(list(reversed(row))))
    return Clues(top=top, bottom=bottom, left=left, right=right)


def _latin_square_solution(n: int, rng: random.Random) -> Grid:
    """
    Create a valid Latin-square-based solution (rows are shifted permutations),
    then randomize via row/col/symbol permutations.
    """
    base = list(range(1, n + 1))
    grid = [base[i:] + base[:i] for i in range(n)]

    # permute symbols
    sym = base[:]
    rng.shuffle(sym)
    mapping = {base[i]: sym[i] for i in range(n)}
    grid = [[mapping[x] for x in row] for row in grid]

    # permute rows and cols
    rows = list(range(n))
    cols = list(range(n))
    rng.shuffle(rows)
    rng.shuffle(cols)
    grid = [[grid[r][c] for c in cols] for r in rows]
    return grid


def _remove_clues_while_unique(n: int, full: Clues, target_nonzero: int, rng: random.Random) -> Clues:
    """
    Greedily remove clues (set to 0) while preserving uniqueness.
    """
    # Flatten clue positions
    positions = []
    for side in ["top", "bottom", "left", "right"]:
        for idx in range(n):
            positions.append((side, idx))
    rng.shuffle(positions)

    # Start with all clues present
    cur = {
        "top": full.top[:],
        "bottom": full.bottom[:],
        "left": full.left[:],
        "right": full.right[:],
    }

    def nonzero_count() -> int:
        return sum(1 for side in cur.values() for v in side if v != 0)

    attempts = 0
    i = 0
    while nonzero_count() > target_nonzero and attempts < 2000 and i < len(positions):
        side, idx = positions[i]
        i += 1
        if cur[side][idx] == 0:
            continue

        # Try remove
        old = cur[side][idx]
        cur[side][idx] = 0
        p = Puzzle(
            n=n,
            clues=Clues(top=cur["top"], bottom=cur["bottom"], left=cur["left"], right=cur["right"]),
            grid=[[0]*n for _ in range(n)],
        )
        count, _, _ = solve_count_solutions(p, max_solutions=2)
        if count != 1:
            # revert
            cur[side][idx] = old
        attempts += 1

    return Clues(top=cur["top"], bottom=cur["bottom"], left=cur["left"], right=cur["right"])


def generate_puzzle(n: int = 4, difficulty: str = "easy", seed: Optional[int] = None) -> Tuple[Puzzle, Grid]:
    """
    Generate a skyscrapers puzzle with a unique solution.
    Returns (puzzle, solution).
    """
    if n not in (4, 5):
        raise ValueError("Only n=4 or n=5 supported in this demo generator.")

    rng = random.Random(seed)

    solution = _latin_square_solution(n, rng)
    full = compute_full_clues(solution)

    # Difficulty maps to how many clues we keep.
    # Total clues = 4*n. For n=4 -> 16.
    # Keep more clues for easy; fewer for hard.
    total = 4 * n
    if difficulty == "easy":
        keep = int(total * 0.75)  # 12 for n=4
    elif difficulty == "medium":
        keep = int(total * 0.62)  # 9-10
    elif difficulty == "hard":
        keep = int(total * 0.50)  # 8
    else:
        raise ValueError("difficulty must be one of: easy, medium, hard")

    keep = max(6, min(total, keep))
    clues = _remove_clues_while_unique(n, full, target_nonzero=keep, rng=rng)

    puzzle = Puzzle(n=n, clues=clues, grid=[[0]*n for _ in range(n)])
    # Sanity: ensure unique
    count, _, _ = solve_count_solutions(puzzle, max_solutions=2)
    if count != 1:
        # fallback: if uniqueness got lost (rare), try again with adjusted keep
        # Keep more clues until unique
        for extra in range(1, total + 1):
            clues2 = _remove_clues_while_unique(n, full, target_nonzero=min(total, keep + extra), rng=rng)
            puzzle2 = Puzzle(n=n, clues=clues2, grid=[[0]*n for _ in range(n)])
            c2, _, _ = solve_count_solutions(puzzle2, max_solutions=2)
            if c2 == 1:
                return puzzle2, solution
        raise RuntimeError("Failed to generate a unique puzzle after retries.")
    return puzzle, solution


def next_single_hint(puzzle: Puzzle) -> Optional[Dict]:
    """
    Return a 'single' hint: find an empty cell where exactly one value keeps the puzzle solvable.
    If none found, return None.
    """
    n = puzzle.n
    grid = [row[:] for row in puzzle.grid]

    # Quick reject: if current grid already invalid (duplicates)
    for i in range(n):
        vals = [v for v in grid[i] if v != 0]
        if len(vals) != len(set(vals)):
            return None
    for j in range(n):
        vals = [grid[i][j] for i in range(n) if grid[i][j] != 0]
        if len(vals) != len(set(vals)):
            return None

    def row_col_ok(i: int, j: int, v: int) -> bool:
        if v in grid[i]:
            return False
        for r in range(n):
            if grid[r][j] == v:
                return False
        return True

    # For each empty cell, test candidates
    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:
                continue
            possible = []
            for v in range(1, n + 1):
                if not row_col_ok(i, j, v):
                    continue
                grid[i][j] = v
                p2 = Puzzle(n=n, clues=puzzle.clues, grid=grid)
                if has_any_solution(p2):
                    possible.append(v)
                grid[i][j] = 0
                if len(possible) > 1:
                    # not a single; stop early
                    pass
            if len(possible) == 1:
                return {
                    "row": i,
                    "col": j,
                    "value": possible[0],
                    "reason": "Only this value keeps the puzzle solvable given current entries and edge clues.",
                }
    return None


def _set_clue(clues: Clues, side: str, idx: int, value: int) -> Clues:
    """Return a new Clues with one clue set (Clues is frozen)."""
    top = clues.top[:]
    bottom = clues.bottom[:]
    left = clues.left[:]
    right = clues.right[:]

    if side == "top":
        top[idx] = value
    elif side == "bottom":
        bottom[idx] = value
    elif side == "left":
        left[idx] = value
    elif side == "right":
        right[idx] = value
    else:
        raise ValueError("side must be one of: top, bottom, left, right")

    return Clues(top=top, bottom=bottom, left=left, right=right)


def reveal_best_clue(puzzle: Puzzle) -> Optional[Dict]:
    """
    Reveal one inner grid value from a valid completion.
    - If unsolvable now, return invalid.
    - Reveals exactly one empty cell.
    """
    n = puzzle.n
    count, sol, _ = solve_count_solutions(puzzle, max_solutions=2)
    if count == 0 or sol is None:
        return {
            "type": "invalid",
            "message": "No solution exists with current entries. Undo a move before revealing a cell.",
        }

    empties: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(n):
            if puzzle.grid[i][j] == 0:
                empties.append((i, j))

    if not empties:
        return {"type": "none", "message": "No empty cells left to reveal."}

    best = None  # (score, row, col, value, post_count)
    for i, j in empties:
        v = sol[i][j]
        g2 = [row[:] for row in puzzle.grid]
        g2[i][j] = v
        p2 = Puzzle(n=n, clues=puzzle.clues, grid=g2)
        post_count, _, _ = solve_count_solutions(p2, max_solutions=2)
        score = 2 if post_count == 1 else 1
        cand = (score, i, j, v, post_count)
        if best is None or cand[0] > best[0]:
            best = cand

    score, row, col, value, post_count = best
    reason = (
        "This revealed value keeps the puzzle uniquely solvable from your current state."
        if score == 2
        else "This revealed value reduces ambiguity from your current state."
    )

    return {
        "type": "reveal",
        "row": row,
        "col": col,
        "value": value,
        "post_solution_count_capped": post_count,
        "reason": reason,
    }
