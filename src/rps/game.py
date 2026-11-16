from dataclasses import dataclass
from typing import Tuple, Set, Optional, Literal, Sequence, AbstractSet

from returns.result import Failure, Result, Success

from rps.graph import RuleGraph
from rps.bots import Bot

Outcome = Literal["win", "lose", "draw"]
WinSide = Literal["first", "second"]
Round = tuple[str, str]


def parse_command(
    raw: str, valid_moves: Set[str], quit_words: Set[str]
) -> Result[Optional[str], str]:
    s = raw.strip().lower()

    if s in quit_words:
        return Success(None)

    if s not in valid_moves:
        allowed = ", ".join(sorted(valid_moves))
        return Failure(f"Invalid move: {raw!r}. Try: {allowed}")

    return Success(s)


def resolve(
    first: str, second: str, rule_graph: RuleGraph
) -> Literal["win", "lose", "draw"]:
    if first == second:
        return "draw"
    return "win" if rule_graph.does_beat(first, second) else "lose"


def validate_moves(moves: AbstractSet[str], rules_name: str) -> None:
    if not moves:
        raise ValueError(f"Rule set {moves!r} contains no moves")
    if any(m != m.lower() for m in moves):
        raise ValueError(
            f"Rule set {moves!r} must contains move names: {sorted(moves)}"
        )


def play_round(
    rule_graph: RuleGraph,
    user: str,
    bot: Bot,
    history: Sequence[Round],
) -> Tuple[str, str, Literal["draw", "win", "lose"]]:
    comp = bot.choose(rule_graph, history)
    if comp not in rule_graph.all_moves():
        raise ValueError(f"Bot {bot.name!r} returned invalid move: {comp!r}")
    return user, comp, resolve(user, comp, rule_graph)


@dataclass
class Score:
    first: int = 0
    second: int = 0
    draws: int = 0

    def record(self, outcome: Literal["win", "lose", "draw"]) -> None:
        match outcome:
            case "win":
                self.first += 1
            case "lose":
                self.second += 1
            case "draw":
                self.draws += 1

    def is_over(self, target: int) -> bool:
        return self.first >= target or self.second >= target

    def rounds_played(self) -> int:
        return self.first + self.second + self.draws

    def winner(self, target: int) -> Optional[WinSide]:
        if self.first >= target:
            return "first"
        if self.second >= target:
            return "second"
        return None

    def __str__(self):
        return f"{self.first}-{self.second} (draws: {self.draws})"
