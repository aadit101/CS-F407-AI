"""STRIPS-style planning agent (BFS) for the warehouse robot - Logical Planning Lab."""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """A planning operator: name, positive/negative preconditions, positive/negative effects."""
    name: str
    pos_pre: frozenset = frozenset()
    neg_pre: frozenset = frozenset()
    pos_eff: frozenset = frozenset()
    neg_eff: frozenset = frozenset()

    def __str__(self):
        return self.name


def fs(*props):
    return frozenset(props)


# ---------------- The warehouse domain ----------------
LOCATIONS = ["A", "B", "C"]
CONNECTED = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]


def move(x, y):
    return Action(f"Move({x},{y})",
                  pos_pre=fs(f"At(Robot,{x})"),
                  pos_eff=fs(f"At(Robot,{y})"),
                  neg_eff=fs(f"At(Robot,{x})"))


def pickup(l):
    return Action(f"PickUp(Package,{l})",
                  pos_pre=fs(f"At(Robot,{l})", f"At(Package,{l})"),
                  pos_eff=fs("Holding(Package)"),
                  neg_eff=fs(f"At(Package,{l})"))


def drop(l):
    return Action(f"Drop(Package,{l})",
                  pos_pre=fs(f"At(Robot,{l})", "Holding(Package)"),
                  pos_eff=fs(f"At(Package,{l})"),
                  neg_eff=fs("Holding(Package)"))


def warehouse_actions(connected=CONNECTED, with_pickup=True, with_drop=True):
    acts = [move(x, y) for x, y in connected]
    if with_pickup:
        acts += [pickup(l) for l in LOCATIONS]
    if with_drop:
        acts += [drop(l) for l in LOCATIONS]
    return acts


INITIAL = fs("At(Robot,A)", "At(Package,A)")
GOAL = fs("At(Package,C)")


# ---------------- Logic: applicability and effects ----------------
def is_applicable(state, action):
    """S |= Preconditions(a): all positive preconditions hold, no negative precondition holds."""
    return action.pos_pre <= state and action.neg_pre.isdisjoint(state)


def apply_action(state, action):
    """S' = Apply(S, a): remove negative effects first, then add positive effects."""
    return (state - action.neg_eff) | action.pos_eff


# ---------------- Search: breadth-first over states ----------------
def bfs_plan(initial, goal, actions, check_preconditions=True):
    """Return dict(found, plan, states, expanded). Shortest plan (fewest actions) if one exists."""
    initial, goal = frozenset(initial), frozenset(goal)
    frontier = deque([initial])
    parent = {initial: None}                      # state -> (previous state, action); doubles as 'visited'
    expanded = 0
    while frontier:
        state = frontier.popleft()
        expanded += 1
        if goal <= state:                         # goal test: S |= G
            plan, states, node = [], [state], state
            while parent[node] is not None:
                node, act = parent[node]
                plan.append(act)
                states.append(node)
            plan.reverse(); states.reverse()
            return {"found": True, "plan": plan, "states": states, "expanded": expanded}
        for act in actions:
            if check_preconditions and not is_applicable(state, act):
                continue                          # logic prunes impossible actions
            nxt = apply_action(state, act)
            if nxt not in parent:                 # never revisit a state
                parent[nxt] = (state, act)
                frontier.append(nxt)
    return {"found": False, "plan": None, "states": None, "expanded": expanded}


def fmt(state):
    return ", ".join(sorted(state)) if state else "(empty)"


def show(result, goal=None):
    if not result["found"]:
        print(f"No plan found  (states expanded: {result['expanded']})")
        return
    print(f"Plan found with {len(result['plan'])} actions (states expanded: {result['expanded']})")
    print(f"  S0: {fmt(result['states'][0])}")
    for i, (a, s) in enumerate(zip(result["plan"], result["states"][1:]), 1):
        print(f"  a{i}: {a}\n  S{i}: {fmt(s)}")


# ---------------- Independent plan checker ----------------
def verify_plan(initial, plan, goal, verbose=True):
    """Replay a plan step by step, checking every precondition explicitly.
    Written separately from bfs_plan so it can act as an independent check on it."""
    state = set(initial)
    for i, act in enumerate(plan, 1):
        missing = [p for p in sorted(act.pos_pre) if p not in state]
        blocked = [p for p in sorted(act.neg_pre) if p in state]
        if missing or blocked:
            if verbose:
                print(f"  step {i}: {act} INVALID - missing {missing or '-'}, forbidden-but-true {blocked or '-'}")
            return False
        state.difference_update(act.neg_eff)
        state.update(act.pos_eff)
        if verbose:
            print(f"  step {i}: {act} ok -> {{{fmt(state)}}}")
    ok = set(goal) <= state
    if verbose:
        print(f"  goal {{{fmt(goal)}}} satisfied: {ok}")
    return ok


def reachable_states(initial, actions):
    initial = frozenset(initial)
    seen, queue = {initial}, deque([initial])
    while queue:
        s = queue.popleft()
        for a in actions:
            if is_applicable(s, a):
                n = apply_action(s, a)
                if n not in seen:
                    seen.add(n); queue.append(n)
    return seen


if __name__ == "__main__":
    acts = warehouse_actions()
    res = bfs_plan(INITIAL, GOAL, acts)
    show(res)
    print("Independent verification:")
    print("VALID" if verify_plan(INITIAL, res["plan"], GOAL) else "INVALID")
