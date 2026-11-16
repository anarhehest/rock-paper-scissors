import argparse
import sys
from dataclasses import dataclass
from typing import Tuple, Set, Optional, Literal

from returns.result import Failure, Result, Success

from colors import Style, supports_color
from graph import build_rule_graph, RuleGraph
from rules import list_available_rules, load_rules


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
    rule_graph: RuleGraph, user: str
) -> Tuple[str, str, Literal["draw", "win", "lose"]]:
    comp = rule_graph.get_random_move()
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
        "--no-color",
        action="store_true",
        help="Disable colored output (also respects NO_COLOR env var)",
    )

    args = parser.parse_args()

    if args.first_to < 1:
        parser.error("--first-to must be at least 1")

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
                    user, comp, result = play_round(rule_graph, move)
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


if __name__ == "__main__":
    main()
