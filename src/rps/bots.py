from __future__ import annotations

import importlib.util
import random
from pathlib import Path
from typing import Protocol, Sequence

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

    def choose(self, rule_graph: RuleGraph, history: Sequence["Round"]) -> str:
        if not history:
            return rule_graph.get_random_move()
        last_user = history[-1][0]
        winners = [
            m for m in rule_graph.all_moves() if rule_graph.does_beat(m, last_user)
        ]
        return random.choice(winners) if winners else rule_graph.get_random_move()


BUILTIN_BOTS: dict[str, Bot] = {b.name: b for b in (RandomBot(), BeatLastBot())}


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
