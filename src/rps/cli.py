import argparse
import sys
from getpass import getpass
from pathlib import Path
from typing import Optional, Set

from returns.result import Failure, Success

from rps.bots import BUILTIN_BOTS, Bot, Round, load_bot_file
from rps.colors import Style, supports_color
from rps.game import Score, parse_command, play_round, resolve
from rps.graph import build_rule_graph
from rps.rules import list_available_rules, load_rules


def _read_pvp_move(prompt: str) -> str:
    if sys.stdin.isatty() and sys.stdout.isatty():
        return getpass(prompt)
    return input(prompt)


def _read_validated_move(
    prompt: str, valid_moves: Set[str], quit_words: Set[str], style: Style
) -> tuple[bool, Optional[str]]:
    try:
        raw = _read_pvp_move(prompt)
    except EOFError:
        return True, None
    match parse_command(raw, valid_moves, quit_words):
        case Success(None):
            return True, None
        case Success(move):
            assert move is not None
            return False, move
        case Failure(msg):
            print(style.red(msg))
            return False, None


def main() -> None:
    possible_rules = list_available_rules()

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

    args = parser.parse_args()

    if args.first_to < 1:
        parser.error("--first-to must be at least 1")

    style = Style(enabled=supports_color() and not args.no_color)

    pvp = args.pvp
    bot: Optional[Bot] = None
    if not pvp:
        if args.bot_file:
            try:
                bot = load_bot_file(args.bot_file)
            except ValueError as e:
                parser.error(str(e))
        else:
            name = args.bot or "random"
            if name not in BUILTIN_BOTS:
                parser.error(
                    f"unknown bot: {name!r}. "
                    f"available: {', '.join(sorted(BUILTIN_BOTS))}"
                )
            bot = BUILTIN_BOTS[name]

    rules_dict = load_rules(args.rules)
    rule_graph = build_rule_graph(rules_dict)
    moves = rule_graph.all_moves()

    if not moves:
        raise ValueError(f"Rule set {args.rules!r} contains no moves")
    if any(m != m.lower() for m in moves):
        raise ValueError(
            f"Rule set {args.rules!r} must use lowercase move names: {sorted(moves)}"
        )

    quit_words = {"q", "quit", "exit"}
    match_mode = args.first_to > 1
    score = Score()
    history: list[Round] = []

    if pvp:
        outcome_lines = {
            "win": style.green("Player 1 wins!"),
            "lose": style.red("Player 2 wins!"),
            "draw": style.yellow("Draw"),
        }
    else:
        outcome_lines = {
            "win": style.green("User wins!"),
            "lose": style.red("User loses!"),
            "draw": style.yellow("Draw"),
        }

    try:
        while not score.is_over(args.first_to):
            if pvp:
                quit_, p1 = _read_validated_move(
                    style.cyan("Player 1, your move: "), moves, quit_words, style
                )
                if quit_:
                    break
                if p1 is None:
                    continue

                quit_, p2 = _read_validated_move(
                    style.cyan("Player 2, your move: "), moves, quit_words, style
                )
                if quit_:
                    break
                if p2 is None:
                    continue

                result = resolve(p1, p2, rule_graph)
                score.record(result)
                history.append((p1, p2))
                print(f"Player 1: {style.cyan(p1)}")
                print(f"Player 2: {style.cyan(p2)}")
                print(outcome_lines[result])
                if match_mode:
                    print(style.dim(f"Score: {score}"))
            else:
                try:
                    raw = input(style.cyan("Your move: "))
                except EOFError:
                    break

                match parse_command(raw, moves, quit_words):
                    case Success(None):
                        break
                    case Success(move):
                        _, comp, result = play_round(
                            rule_graph, move, bot, history
                        )
                        history.append((move, comp))
                        score.record(result)
                        print(f"Computer's move: {style.cyan(comp)}")
                        print(outcome_lines[result])
                        if match_mode:
                            print(style.dim(f"Score: {score}"))
                    case Failure(msg):
                        print(style.red(msg))

    except KeyboardInterrupt:
        sys.exit(130)

    if match_mode and score.rounds_played() > 0:
        print()
        print(style.dim(f"Final score: {score}"))
        if not score.is_over(args.first_to):
            print(style.yellow("Match abandoned."))
        elif score.user > score.comp:
            label = "Player 1" if pvp else "User"
            print(style.bold_green(f"{label} wins the match!"))
        else:
            label = "Player 2" if pvp else "Computer"
            print(style.bold_red(f"{label} wins the match!"))