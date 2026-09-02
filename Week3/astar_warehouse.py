"""A* search for the warehouse robot (Search Laboratory)."""
import heapq
import math
from collections import deque

WAREHOUSE = """
#################
#S....#.........#
#.###.#.#######.#
#...#.#.......#.#
###.#.#######.#.#
#...#.........#.#
#.###########.#.#
#.............#G#
#################
"""

class Grid:
    """The warehouse: a 2D grid plus the search-problem interface
    (initial state, actions/transitions, goal test, step cost)."""

    MOVES = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}

    def __init__(self, text):
        self.cells = [list(row) for row in text.strip().splitlines()]
        self.rows, self.cols = len(self.cells), len(self.cells[0])
        self.start = self._find("S")
        self.goal = self._find("G")

    def _find(self, ch):
        for r, row in enumerate(self.cells):
            for c, v in enumerate(row):
                if v == ch:
                    return (r, c)
        raise ValueError(f"Map has no '{ch}'")

    def is_free(self, s):
        r, c = s
        return 0 <= r < self.rows and 0 <= c < self.cols and self.cells[r][c] != "#"

    def neighbours(self, s):
        """Yield (action, next_state, step_cost) for every VALID action in state s."""
        for action, (dr, dc) in self.MOVES.items():
            nxt = (s[0] + dr, s[1] + dc)
            if self.is_free(nxt):
                yield action, nxt, 1

    def is_goal(self, s):
        return s == self.goal

    def render(self, path=()):
        canvas = [row[:] for row in self.cells]
        for (r, c) in path:
            if canvas[r][c] == ".":
                canvas[r][c] = "*"
        return "\n".join("".join(row) for row in canvas)


# ---- Heuristics: each takes (state, goal) and estimates the remaining cost ----
def manhattan(s, g):  return abs(s[0] - g[0]) + abs(s[1] - g[1])
def euclidean(s, g):  return math.hypot(s[0] - g[0], s[1] - g[1])
def zero(s, g):       return 0

def astar(grid, h=manhattan, tie_break="h"):
    """
    A* search.  f(n) = g(n) + h(n)
    Returns a dict: found, path, length, expanded.

    tie_break="h"    : among equal f, expand the state with smaller h first
    tie_break="fifo" : among equal f, expand the oldest state first
    """
    start, goal = grid.start, grid.goal
    counter = 0                                    # final tie-breaker; avoids comparing states
    h0 = h(start, goal)
    frontier = [(h0, h0, counter, 0, start)]       # (f, h, counter, g, state) - a min-heap
    parent = {start: None}                         # for path reconstruction
    best_g = {start: 0}                            # cheapest known g for each state
    closed = set()                                 # states already expanded
    expanded = 0

    while frontier:
        f, _, _, g, state = heapq.heappop(frontier)      # lowest f first
        if state in closed:                              # stale duplicate entry -> skip
            continue
        closed.add(state)
        expanded += 1

        if grid.is_goal(state):                          # goal test on EXPANSION
            path, node = [], state
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return {"found": True, "path": path, "length": g, "expanded": expanded}

        for action, nxt, cost in grid.neighbours(state):
            g_new = g + cost
            if nxt not in best_g or g_new < best_g[nxt]: # found a cheaper way to nxt
                best_g[nxt] = g_new
                parent[nxt] = state
                counter += 1
                h_new = h(nxt, goal)
                f_new = g_new + h_new                    # f(n) = g(n) + h(n)
                heapq.heappush(frontier, (f_new, h_new if tie_break == "h" else 0, counter, g_new, nxt))

    return {"found": False, "path": None, "length": None, "expanded": expanded}


def report(grid, result, name="A*"):
    print(f"[{name}] Solution found: {result['found']}")
    print(f"[{name}] States expanded: {result['expanded']}")
    if result["found"]:
        print(f"[{name}] Path length: {result['length']}")
        print(f"[{name}] Path: {result['path']}")
        print(grid.render(result["path"]))

def bfs(grid):
    """Breadth-first search, returning the same result format as astar()."""
    start = grid.start
    queue, parent, expanded = deque([start]), {start: None}, 0
    while queue:
        state = queue.popleft()
        expanded += 1
        if grid.is_goal(state):
            path, node = [], state
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return {"found": True, "path": path, "length": len(path) - 1, "expanded": expanded}
        for _, nxt, _ in grid.neighbours(state):
            if nxt not in parent:
                parent[nxt] = state
                queue.append(nxt)
    return {"found": False, "path": None, "length": None, "expanded": expanded}


if __name__ == "__main__":
    warehouse = Grid(WAREHOUSE)
    report(warehouse, astar(warehouse), "A*")
    print()
    report(warehouse, bfs(warehouse), "BFS")
