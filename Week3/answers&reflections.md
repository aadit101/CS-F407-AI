| File | Contents |
|---|---|
| `search_astar_lab.ipynb` | Full lab: formulation, design, code, tests, comparisons, reflections |
| `astar_warehouse.py` | Final standalone Python program (A* + BFS); run with `python astar_warehouse.py` |
| `answers&reflections.md` | This report (summary of results and answers) |

## 1. Formulation of the search problem (Task 0)

| Component | Specification |
|---|---|
| State S | Robot position `(row, col)` on a free cell |
| Actions A | Up, Down, Left, Right |
| Transition T | `(r,c) → (r+dr, c+dc)` if in bounds and not `#`; otherwise action invalid |
| Initial state s₀ | Position of `S` = `(1, 1)` |
| Goal G | `{(7, 15)}`; goal test `state == goal` |
| Cost c | 1 per move |

- **(a) State information:** only the position; the map is static and fully known.
- **(b) Invalid action:** moving into `#` or outside the grid.
- **(c) Deterministic?** Yes: one outcome per action, fully known static map, single agent.
- **(d) Solution:** a sequence of valid moves from `S` to `G`; optimal = fewest moves.

## 2. Design of the agent (Task 1)

1. State: a `(row, col)` tuple (hashable, so usable in sets and dicts).
2. Warehouse: `Grid` class holding a list of lists of characters, with `start` and `goal` located by scanning.
3. Valid actions: `Grid.neighbours(state)` yields `(action, next_state, cost)` for in-bounds, non-`#` cells.
4. Goal recognition: `is_goal(state)`, tested when a state is **popped** from the frontier (needed for optimality).
5. Frontier: min-heap of `(f, h, counter, g, state)`; `h` and `counter` are tie-breakers.
6. Path reconstruction: `parent` dict; follow it back from the goal and reverse.

Bookkeeping: `best_g` (cheapest known cost per state) and a `closed` set (expanded states). The program reports: found or not, the path, its length, and the number of states expanded.

## 3. Prompts used (Task 2)

1. **Initial:** *"I am implementing a simple goal-based search agent in Python. The environment is a grid represented by an ASCII map. The agent starts at S and must reach G. `#` are obstacles and `.` free cells. The agent can move up, down, left or right; every move costs 1. Implement A* search with Manhattan distance as the heuristic. The program should: represent grid positions as states; maintain an appropriate frontier; calculate g(n), h(n) and f(n); avoid repeatedly expanding the same state; reconstruct the path when the goal is reached; report the path and its length; report the number of states expanded. Keep it simple and explain the main components."*
2. "Make the heuristic a function parameter."
3. "Add a BFS version returning the same result format."
4. "Among states with equal f, prefer the one with smaller h."
5. "Explain why Manhattan distance is admissible for 4-direction grid movement." (asked only after my own experiments)

## 4. Test results (Task 3)

| Test | Map | Expected | Result |
|---|---|---|---|
| 1 Original | Lab warehouse | Path exists | **Found**, length **40**, **64** states expanded |
| 2 Trivial | `#####/#SG##/#####` | 1 move | **Found**, length 1, 2 expanded |
| 3 No solution | `#######/#S....#/###.###/#...#G#/#######` | Failure, no infinite loop | **Not found**, terminated after 9 expansions |
| 4 Alternative paths | Two routes (lengths 4 and 8) | Shortest (4) | **Length 4** |
| Extra | 500 random 8×12 grids | A* agrees with BFS on solvability and length | **All 500 agree** (248 solvable, 252 not) |

Test 1 path: Right×4, Down×4, Right×8, Up×2, Left×6, Up×2, Right×8, Down×6.

```
#################
#S****#*********#
#.###*#*#######*#
#...#*#*******#*#
###.#*#######*#*#
#...#*********#*#
#.###########.#*#
#.............#G#
#################
```

## 5. Code inspection (Task 4)

| Concept | Where in the code |
|---|---|
| State | `(row, col)` tuple |
| Action | Keys of `Grid.MOVES` |
| Transition | `Grid.neighbours` (`nxt = (s[0]+dr, s[1]+dc)`) |
| Goal test | `grid.is_goal(state)` after `heappop` |
| g(n) | `g` in the heap entry; `g_new = g + cost`; best values in `best_g` |
| h(n) | `h(nxt, goal)` (default `manhattan`) |
| f(n) | `f_new = g_new + h_new`, first element of the heap entry |
| Frontier | `frontier` list used as a `heapq` min-heap |
| Visited | `closed` set + `best_g` |
| Path reconstruction | `parent` dict, walked back from the goal |

- **(a)** Binary min-heap (priority queue) via `heapq`.
- **(b)** `heappop` returns the smallest `f`; ties go to smaller `h`, then insertion order.
- **(c)** `h_new = h(nxt, goal)` in `astar`, using `manhattan`.
- **(d)** Yes, `f_new = g_new + h_new`.
- **(e)** `closed` set skips already-expanded states; `best_g` allows a push only for new or strictly cheaper routes; stale duplicate heap entries are skipped ("lazy deletion").

## 6. BFS vs A* (Task 5)

**Lab warehouse**

| Measure | BFS | A* |
|---|---|---|
| Solution found | Yes | Yes |
| Path length | 40 | 40 |
| States expanded | 64 | 64 |

- **(a)** Both found a solution. **(b)** Same length (40), optimal.
- **(c)** Neither expanded fewer: A* gave **no advantage** on this map.
- **(d)** In general A* expands fewer states because the heuristic steers it towards the goal instead of expanding evenly in all directions. Here the map is a serpentine maze: the true route is 40 moves, but the Manhattan distance from `S` to `G` is only 20 and the route must first move away from the goal, so the heuristic misleads and A* explores every corridor.

**Extra experiment: open room** (S top-left, G bottom-right, one block in the middle)

| Measure | BFS | A* |
|---|---|---|
| Path length | 17 | 17 |
| States expanded | 70 | **18** |

**Tie-breaking finding:** with FIFO tie-breaking, A* expanded all 70 cells in the open room (identical to BFS) because many cells share the same `f`. Preferring smaller `h` among ties reduced this to 18. This was a design weakness in the first version which correctness tests could not reveal, only comparing the number of expanded states did.

## 7. Heuristic investigation (Task 6)

Manhattan is admissible (each move reduces |Δrow|+|Δcol| by at most 1, so it never overestimates) and consistent.

| Heuristic | Warehouse (opt. 40): length / expanded | Open room (opt. 17): length / expanded |
|---|---|---|
| h = 0 | 40 / 64 | 17 / 70 |
| Manhattan | 40 / 64 | 17 / 18 |
| Euclidean | 40 / 64 | 17 / 54 |
| 2 × Manhattan | 40 / 64 | 17 / 18 |
| 3 × Manhattan | **48** / 64 | 17 / 18 |
| 5 × Manhattan | **48** / 64 | 17 / 18 |
| 10 × Manhattan | **48** / 58 | 17 / 18 |

All versions found a solution.

1. **h = 0:** still optimal (admissible) but uninformed, so A* becomes uniform-cost search, equal to BFS here.
2. **Euclidean:** admissible and optimal, but always ≤ Manhattan, so guidance is weaker: 54 expansions vs 18 in the open room.
3. **Scaled ×2 and above:** not admissible. On the warehouse ×2 still happened to return 40, but ×3 and up returned a suboptimal **48-move** path. On the open room there was no harm since the greedy route is also optimal. So an overestimating heuristic *allows* suboptimal answers; whether it occurs depends on the map.

**Conclusion:** too optimistic / weak → optimal but wasteful; too aggressive → possibly faster but no optimality guarantee, and no error message to warn you.

## 8. Evaluating the LLM-generated agent (Task 7, draft – edit to reflect your experience)

1. **Correct immediately:** overall structure (`Grid`, `heapq` frontier, `closed`, `parent`, reporting); Tests 1–4 passed unchanged.
2. **Problems found:** tie-breaking by insertion order made A* behave like BFS on the open room (70 expansions).
3. **How discovered:** by comparing states expanded against BFS on a map where A* should win; not by path-correctness tests.
4. **Unfamiliar terms:** consistent heuristic, lazy deletion, closed set, tie-breaking counter.
5. **Modifications:** heuristic as parameter, `h` tie-break, BFS version, `assert`-based tests.
6. **Most useful tests:** BFS cross-check on random grids; unreachable-goal test; BFS-vs-A* state counts.
7. **Trust without testing?** No; it ran first time and looked right, yet had an efficiency weakness, and small heuristic changes silently gave wrong (suboptimal) answers.
8. **Learned about A\*:** `f = g + h` bounds the best solution through a node; the goal test belongs at expansion; admissibility guarantees optimality; a good heuristic can still be useless in a maze; tie-breaking matters.

| | |
|---|---|
| **Designed by me** | Problem formulation, agent design, test plan, heuristic experiments |
| **Suggested by LLM** | Initial code, data structures, BFS version, explanations |
| **Accepted** | Core A* loop, grid/neighbour logic, path reconstruction |
| **Changed** | Heuristic parameter, tie-breaking, reporting, tests |
| **Tested** | Original, trivial, unreachable, alternative paths, 500 random grids vs BFS, BFS vs A*, 7 heuristics × 2 maps |

## 9. Final reflection

**1. Why formulate the problem first?** The formulation (states, actions, transitions, initial state, goal, cost) is what any search algorithm consumes. With it precise, the algorithm is generic and interchangeable (BFS, A*). Without it, the code hides assumptions and there is no basis to judge correctness. It is also the part an LLM cannot reliably do for you.

**2. In what sense is A\* informed?** BFS uses only the structure of the problem (steps from the start). A* also uses problem-specific knowledge, a heuristic estimate of the remaining cost, and orders the frontier by `f = g + h`. Its efficiency depends on the quality of that knowledge.

**3. Why does the heuristic matter?** It controls both correctness and efficiency: admissible keeps A* optimal, tighter means fewer expansions (Manhattan 18, Euclidean 54, zero 70 in the open room), while overestimating risks suboptimal paths (48 vs 40). Even a good heuristic can mislead in a maze (A* = BFS = 64 states).

**4. What did the LLM contribute?** A quick working, structured implementation with standard patterns, the BFS variant and explanations of terminology. It did not decide what the problem was, verify itself, or flag the tie-breaking inefficiency; those came from design, testing and measurement.

**5. What could go wrong without testing?** Non-shortest paths, infinite loops on unreachable goals, goal tests at generation time (breaking optimality), inadmissible heuristics, or wasted work from poor tie-breaking, none of which raise errors. Working output ≠ validated algorithm.

