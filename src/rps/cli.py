import argparse
import sys
from pathlib import Path

from returns.result import Failure, Success

from rps.colors import Style, supports_color
from rps.graph import build_rule_graph
from rps.rules import list_available_rules, load_rules
from rps.game import Score, parse_command, play_round
from rps.bots import BUILTIN_BOTS, load_bot_file


def main():
    possible_rules = list_available_rules()

    parser = argparse.ArgumentParser(
        description="Rock, Paper, Scissors, etc.",
        epilog=f"Possible rules sets: {', '.join(possible_rules)}",
    )

    parser.add_argument(
        "rules",
        metavar="RULES",
        type=str,
        choices=possible_rules,
    )
    parser.add_argument(
        "--first-to",
        metavar="N",
        type=int,
        default=1,
        help="Play until either side wins N rounds (default: 1)",
    )
    parser.add_argument(
        "--bot",
        default="random",
        metavar="NAME",
        help=f"Bot to play against: {', '.join(sorted(BUILTIN_BOTS))} (default: random)",
    )
    parser.add_argument(
        "--bot-file",
        type=Path,
        metavar="PATH",
        help="Load a custom bot from a Python file (overrides --bot)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output (also respects NO_COLOR env var)",
    )

    args = parser.parse_args()

    if args.first_to < 1:
        parser.error("--first-to must be at least 1")

    if args.bot_file:
        try:
            bot = load_bot_file(args.bot_file)
        except ValueError as e:
            parser.error(str(e))
    elif args.bot in BUILTIN_BOTS:
        bot = BUILTIN_BOTS[args.bot]
    else:
        parser.error(
            f"unknown bot: {args.bot!r}. available: {', '.join(sorted(BUILTIN_BOTS))}"
        )

    style = Style(enabled=supports_color() and not args.no_color)

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
    outcomes = {
        "win": style.green("User wins!"),
        "lose": style.red("User loses!"),
        "draw": style.yellow("Draw")
    }

    score = Score()
    history: list[tuple[str, str]] = []
    match_mode = args.first_to > 1
    prompt = style.cyan("Your move: ")

    try:
        while not score.is_over(args.first_to):
            try:
                raw = input(prompt)
            except EOFError:
                break

            match parse_command(raw, moves, quit_words):
                case Success(None):
                    break

                case Success(move):
                    user, comp, result = play_round(rule_graph, move, bot, history)
                    history.append((move, comp))
                    score.record(result)

                    print(f"Computer's move: {comp}")
                    print(outcomes[result])
                    if match_mode:
                        print(f"Score: {score}")

                case Failure(msg):
                    print(msg)

    except KeyboardInterrupt:
        sys.exit(130)

    if match_mode and score.rounds_played() > 0:
        print()
        print(style.dim(f"Final score: {score}"))
        if not score.is_over(args.first_to):
            print(style.yellow("Match abandoned."))
        elif score.user > score.comp:
            print(style.bold_green("User wins the match!"))
        else:
            print(style.bold_red("Computer wins the match!"))
