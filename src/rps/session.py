import sys
from getpass import getpass
from typing import Optional

from returns.result import Failure, Result, Success

from rps.bots import Bot
from rps.colors import Style
from rps.game import Outcome, Round, Score, parse_command, resolve
from rps.graph import RuleGraph

MoveResult = Result[Optional[str], str]
Labels = tuple[str, str]

QUIT_WORDS: frozenset[str] = frozenset({"q", "quit", "exit"})


def _read_move(prompt: str, hide: bool) -> str:
    if hide and sys.stdin.isatty() and sys.stdout.isatty():
        return getpass(prompt)
    return input(prompt)


def _read_validated_move(
    prompt: str,
    valid_moves: frozenset[str],
    quit_words: frozenset[str],
    style: Style,
    hide: bool = False,
) -> MoveResult:
    try:
        raw = _read_move(prompt, hide)
    except EOFError:
        return Success(None)
    result = parse_command(raw, valid_moves, quit_words)
    if isinstance(result, Failure):
        print(style.red(result.failure()))
    return result


def _outcome_lines(style: Style, labels: Labels) -> dict[Outcome, str]:
    return {
        "win": style.green(f"{labels[0]} wins!"),
        "lose": style.red(f"{labels[1]} wins!"),
        "draw": style.yellow("Draw"),
    }


def _print_round(
    first_move: str,
    second_move: str,
    result: Outcome,
    score: Score,
    match_mode: bool,
    style: Style,
    labels: Labels,
    outcome_lines: dict[Outcome, str],
) -> None:
    print(f"{labels[0]}: {style.cyan(first_move)}")
    print(f"{labels[1]}: {style.cyan(second_move)}")
    print(outcome_lines[result])
    if match_mode:
        print(style.dim(f"Score: {score}"))


def run_pve(rule_graph: RuleGraph, bot: Bot, first_to: int, style: Style) -> Score:
    labels: Labels = ("User", "Computer")
    moves = rule_graph.all_moves()
    outcome_lines = _outcome_lines(style, labels)
    match_mode = first_to > 1
    score = Score()
    history: list[Round] = []

    while not score.is_over(first_to):
        match _read_validated_move(
            style.cyan("Your move: "),
            moves,
            QUIT_WORDS,
            style,
        ):
            case Success(None):
                break
            case Success(move):
                assert move is not None
                opponent = bot.choose(rule_graph, history)
                if opponent not in moves:
                    raise ValueError(
                        f"Bot {bot.name!r} returned invalid move: {opponent!r}"
                    )
                result = resolve(move, opponent, rule_graph)
                score.record(result)
                history.append((move, opponent))
                _print_round(
                    move,
                    opponent,
                    result,
                    score,
                    match_mode,
                    style,
                    labels,
                    outcome_lines,
                )
            case Failure(_):
                continue

    return score


def run_pvp(rule_graph: RuleGraph, first_to: int, style: Style) -> Score:
    labels: Labels = ("Player 1", "Player 2")
    moves = rule_graph.all_moves()
    outcome_lines = _outcome_lines(style, labels)
    match_mode = first_to > 1
    score = Score()
    history: list[Round] = []

    while not score.is_over(first_to):
        match _read_validated_move(
            style.cyan("Player 1, your move: "), moves, QUIT_WORDS, style, hide=True
        ):
            case Success(None):
                return score
            case Success(first_move):
                assert first_move is not None
            case Failure(_):
                continue

        match _read_validated_move(
            style.cyan("Player 2, your move: "), moves, QUIT_WORDS, style, hide=True
        ):
            case Success(None):
                return score
            case Success(second_move):
                assert second_move is not None
            case Failure(_):
                continue

        result = resolve(first_move, second_move, rule_graph)
        score.record(result)
        history.append((first_move, second_move))
        _print_round(
            first_move,
            second_move,
            result,
            score,
            match_mode,
            style,
            labels,
            outcome_lines,
        )

    return score


def print_match_result(
    score: Score, first_to: int, style: Style, labels: Labels
) -> None:
    if first_to <= 1 or score.rounds_played() == 0:
        return
    print()
    print(style.dim(f"Final score: {score}"))
    winner = score.winner(first_to)
    if winner is None:
        print(style.yellow("Match abandoned."))
        return
    label = labels[0] if winner == "first" else labels[1]
    color = style.bold_green if winner == "first" else style.bold_red
    print(color(f"{label} wins the match!"))
