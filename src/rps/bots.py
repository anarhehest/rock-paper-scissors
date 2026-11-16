from __future__ import annotations

import importlib.util
import random
from pathlib import Path
from typing import Protocol, Sequence, Optional, Callable

from rps.graph import RuleGraph


class Bot(Protocol):
    name: str

    def choose(self, rule_graph: RuleGraph, history: Sequence["Round"]) -> str: ...


class RandomBot:
    name = "random"

    def choose(self, rule_graph: RuleGraph, history: Sequence["Round"]) -> str:
        return rule_graph.get_random_move()


class BeatLastBot:
    name = "beat-last"

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng if rng is not None else random.Random()

    def choose(self, rule_graph: RuleGraph, history: Sequence["Round"]) -> str:
        if not history:
            return rule_graph.get_random_move()
        last_user = history[-1][0]
        winners = [
            m for m in rule_graph.all_moves() if rule_graph.does_beat(m, last_user)
        ]
        return self._rng.choice(winners) if winners else rule_graph.get_random_move()


BotFactory = Callable[[random.Random], Bot]

BUILTIN_BOTS: dict[str, BotFactory] = {
    "random": lambda rng: RandomBot(),
    "beat-last": lambda rng: BeatLastBot(),
}


def make_bot(name: str, rng: random.Random) -> Bot:
    if name not in BUILTIN_BOTS:
        raise KeyError(name)
    return BUILTIN_BOTS[name](rng)


def load_bot_file(path: Path) -> Bot:
    if not path.is_file():
        raise ValueError(f"Bot file not found: {path}")

    spec = importlib.util.spec_from_file_location(f"_custom_bot_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load bot from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    bot = getattr(module, "BOT", None)
    if bot is None:
        raise ValueError(f"{path}: missing BOT object")
    if not hasattr(bot, "name") or not hasattr(bot, "choose"):
        raise ValueError(f"{path}: BOT must have 'name' and 'choose'")

    return bot
