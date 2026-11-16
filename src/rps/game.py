from dataclasses import dataclass
from typing import Tuple, Set, Optional, Literal, Sequence

from returns.result import Failure, Result, Success

from rps.graph import RuleGraph
from rps.bots import Bot, Round


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
    user: str, comp: str, rule_graph: RuleGraph
) -> Literal["win", "lose", "draw"]:
    if user == comp:
        return "draw"
    return "win" if rule_graph.does_beat(user, comp) else "lose"


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
    user: int = 0
    comp: int = 0
    draws: int = 0

    def record(self, outcome: Literal["win", "lose", "draw"]) -> None:
        match outcome:
            case "win":
                self.user += 1
            case "lose":
                self.comp += 1
            case "draw":
                self.draws += 1

    def is_over(self, target: int) -> bool:
        return self.user >= target or self.comp >= target

    def rounds_played(self) -> int:
        return self.user + self.comp + self.draws

    def __str__(self):
        return f"{self.user}-{self.comp} (draws: {self.draws})"
