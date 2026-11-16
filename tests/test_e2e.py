import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent


def run_game(args, stdin="", env_extra=None):
    env = {**os.environ, **(env_extra or {})}
    return subprocess.run(
        [sys.executable, "main.py", *args],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=10,
        env=env,
    )


def test_quit_exits_zero():
    r = run_game(["classic"], stdin="q\n")
    assert r.returncode == 0


def test_eof_exits_zero():
    r = run_game(["classic"], stdin="")
    assert r.returncode == 0


def test_invalid_move_prints_hint():
    r = run_game(["classic"], stdin="banana\nq\n")
    assert r.returncode == 0
    assert "Invalid move" in r.stdout
    assert "rock" in r.stdout


def test_play_round_prints_result():
    r = run_game(["classic"], stdin="rock\nq\n")
    assert r.returncode == 0
    assert "Computer's move:" in r.stdout
    assert any(s in r.stdout for s in ["Draw", "User wins!", "User loses!"]), (
        f"unexpected output: {r.stdout!r}"
    )


def test_case_insensitive_input():
    r = run_game(["classic"], stdin="  ROCK  \nq\n")
    assert r.returncode == 0
    assert "Invalid move" not in r.stdout


def test_help_lists_rules():
    r = run_game(["--help"])
    assert r.returncode == 0
    assert "classic" in r.stdout
    assert "startrek" in r.stdout


def test_missing_rules_arg_exits_two():
    r = run_game([])
    assert r.returncode == 2


def test_unknown_rules_arg_exits_two():
    r = run_game(["nope"])
    assert r.returncode == 2


def test_first_to_zero_rejected():
    r = run_game(["classic", "--first-to", "0"])
    assert r.returncode == 2


def test_first_to_negative_rejected():
    r = run_game(["classic", "--first-to", "-1"])
    assert r.returncode == 2


def test_first_to_non_int_rejected():
    r = run_game(["classic", "--first-to", "abc"])
    assert r.returncode == 2


def test_default_mode_has_no_final_line():
    r = run_game(["classic"], stdin="rock\nq\n")
    assert r.returncode == 0
    assert "Final score:" not in r.stdout


def test_quit_midway_shows_abandoned():
    r = run_game(["classic", "--first-to", "5"], stdin="rock\nq\n")
    assert r.returncode == 0
    assert "Final score:" in r.stdout
    assert "abandoned" in r.stdout.lower()


def test_match_completes_and_declares_winner():
    # 20 rounds is more than enough: P(not finishing) is astronomically small
    r = run_game(["classic", "--first-to", "3"], stdin="rock\n" * 20 + "q\n")
    assert r.returncode == 0
    assert "wins the match!" in r.stdout


def test_pipe_has_no_ansi_by_default():
    r = run_game(["classic"], stdin="rock\nq\n")
    assert "\033[" not in r.stdout


def test_force_color_env_produces_ansi():
    r = run_game(["classic"], stdin="rock\nq\n", env_extra={"FORCE_COLOR": "1"})
    assert "\033[" in r.stdout


def test_no_color_flag_disables_ansi_despite_force():
    r = run_game(
        ["classic", "--no-color"],
        stdin="rock\nq\n",
        env_extra={"FORCE_COLOR": "1"},
    )
    assert "\033[" not in r.stdout


def test_no_color_env_disables_ansi():
    r = run_game(
        ["classic"],
        stdin="rock\nq\n",
        env_extra={"NO_COLOR": "1", "FORCE_COLOR": "1"},
    )
    assert "\033[" not in r.stdout
