import pytest
from returns.result import Success, Failure

from main import parse_command

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
