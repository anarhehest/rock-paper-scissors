import argparse
import sys
from pathlib import Path
from typing import Optional

from rps.bots import BUILTIN_BOTS, Bot, load_bot_file
from rps.colors import Style, supports_color
from rps.game import validate_moves
from rps.graph import build_rule_graph
from rps.rules import list_available_rules, load_rules
from rps.session import run_pvp, run_pve, print_match_result


def _build_parser(possible_rules: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rock, Paper, Scissors, etc.",
        epilog=f"Possible rules sets: {', '.join(possible_rules)}",
    )
    parser.add_argument("rules", metavar="RULES", type=str, choices=possible_rules)
    parser.add_argument(
        "--first-to",
        metavar="N",
        type=int,
        default=1,
        help="Play until either side wins N rounds (default: 1)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output (also respects NO_COLOR env var)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--pvp", action="store_true", help="Two-player hot-seat mode")
    mode.add_argument(
        "--bot",
        default=None,
        metavar="NAME",
        help=f"Bot to play against (default: random). "
        f"Available: {', '.join(sorted(BUILTIN_BOTS))}",
    )
    mode.add_argument(
        "--bot-file",
        type=Path,
        metavar="PATH",
        help="Load a custom bot from a Python file",
    )
    return parser


def _build_bot(
    parser: argparse.ArgumentParser, args: argparse.Namespace
) -> Optional[Bot]:
    if args.pvp:
        return None
    if args.bot_file:
        try:
            return load_bot_file(args.bot_file)
        except ValueError as e:
            parser.error(str(e))
    name = args.bot or "random"
    if name not in BUILTIN_BOTS:
        parser.error(
            f"unknown bot: {name!r}.available: {', '.join(sorted(BUILTIN_BOTS))}"
        )
    return BUILTIN_BOTS[name]


def main() -> None:
    possible_rules = list_available_rules()
    parser = _build_parser(possible_rules)
    args = parser.parse_args()

    if args.first_to < 1:
        parser.error("--first-to must be at least 1")

    style = Style(enabled=supports_color() and not args.no_color)
    bot = _build_bot(parser, args)

    rule_graph = build_rule_graph(load_rules(args.rules))
    validate_moves(rule_graph.all_moves(), args.rules)

    try:
        if args.pvp:
            score = run_pvp(rule_graph, args.first_to, style)
            labels: tuple[str, str] = ("Player 1", "Player 2")
        else:
            assert bot is not None
            score = run_pve(rule_graph, bot, args.first_to, style)
            labels: tuple[str, str] = ("User", "Computer")
    except KeyboardInterrupt:
        sys.exit(130)

    print_match_result(score, args.first_to, style, labels)
