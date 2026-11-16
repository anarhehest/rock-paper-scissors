import random
from collections import defaultdict
from typing import Dict, List, Set


class RuleGraph:
    def __init__(self) -> None:
        self.graph: Dict[str, Set[str]] = defaultdict(set)

    def add_move(self, move: str) -> None:
        self.graph.setdefault(move, set())

    def add_rule(self, winner: str, loser: str) -> None:
        if winner == loser:
            raise ValueError(f"Move {winner!r} cannot beat itself")
        self.add_move(winner)
        self.add_move(loser)
        self.graph[winner].add(loser)

    def does_beat(self, move_a: str, move_b: str) -> bool:
        return move_b in self.graph.get(move_a, set())

    def is_valid_move(self, move: str) -> bool:
        return move in self.graph

    def all_moves(self) -> Set[str]:
        return set(self.graph.keys())

    def get_random_move(self) -> str:
        if not self.graph:
            raise ValueError("Rule graph is empty: no moves to choose from")
        return random.choice(list(self.graph.keys()))

    def __repr__(self) -> str:
        return f"RuleGraph:({dict(self.graph)!r})"


def build_rule_graph(rules_dict: Dict[str, List[str]]) -> RuleGraph:
    graph = RuleGraph()
    for winner, losers in rules_dict.items():
        for loser in losers:
            graph.add_rule(winner, loser)
    return graph
