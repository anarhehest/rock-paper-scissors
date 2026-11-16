import pytest
from returns.result import Failure, Success

from rps.game import Score, parse_command

VALID = {"rock", "paper", "scissors"}
QUIT = {"q", "quit", "exit"}


def apply_match(raw: str) -> str:
    match parse_command(raw, VALID, QUIT):
        case Success(None):
            return "quit"
        case Success(move):
            return f"move:{move}"
        case Failure(msg):
            return f"error:{msg}"
    return "unreachable"


def test_quit_returns_none():
    assert parse_command("q", VALID, QUIT) == Success(None)
    assert apply_match("q") == "quit"


def test_valid_move_returns_canonical_lowercase():
    assert parse_command("  ROCK  ", VALID, QUIT) == Success("rock")
    assert apply_match("rock") == "move:rock"


def test_invalid_move_returns_failure_with_hint():
    result = parse_command("banana", VALID, QUIT)
    assert isinstance(result, Failure)
    assert "Invalid move" in result.failure()
    assert apply_match("banana").startswith("error:")


def test_all_three_branches_are_matched():
    for raw, expected_prefix in [
        ("q", "quit"),
        ("rock", "move:"),
        ("banana", "error:"),
    ]:
        assert apply_match(raw) != "unreachable", f"branch not matched for {raw!r}"
        assert apply_match(raw).startswith(expected_prefix)


def test_returns_exposes_match_args():
    assert hasattr(Success, "__match_args__") or hasattr(Success(1), "__match_args__")
    assert hasattr(Failure, "__match_args__") or hasattr(Failure("x"), "__match_args__")


def test_success_match_args_is_inner_value():
    args = getattr(Success, "__match_args__", None) or Success(1).__match_args__
    assert args == ("_inner_value",), f"returns changed __match_args__: {args!r}"




def test_score_initial():
    s = Score()
    assert (s.user, s.comp, s.draws) == (0, 0, 0)
    assert s.rounds_played() == 0


def test_score_record_win():
    s = Score()
    s.record("win")
    assert (s.user, s.comp, s.draws) == (1, 0, 0)


def test_score_record_lose():
    s = Score()
    s.record("lose")
    assert (s.user, s.comp, s.draws) == (0, 1, 0)


def test_score_record_draw():
    s = Score()
    s.record("draw")
    assert (s.user, s.comp, s.draws) == (0, 0, 1)


def test_score_is_over_user():
    assert Score(user=3, comp=1).is_over(3)
    assert not Score(user=2, comp=2).is_over(3)


def test_score_is_over_comp():
    assert Score(user=1, comp=3).is_over(3)
    assert not Score(user=0, comp=2).is_over(3)


def test_score_is_over_draws_do_not_count():
    assert not Score(draws=100).is_over(1)


def test_score_str():
    assert str(Score(user=2, comp=1, draws=3)) == "2-1 (draws: 3)"
