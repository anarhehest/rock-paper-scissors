import os
import sys

from colors import Style, supports_color


def test_disabled_returns_plain():
    s = Style(enabled=False)
    assert s.green("x") == "x"
    assert s.red("x") == "x"
    assert s.bold_green("x") == "x"


def test_enabled_wraps_with_ansi():
    s = Style(enabled=True)
    assert s.green("x") == "\033[32mx\033[0m"
    assert s.red("x") == "\033[31mx\033[0m"
    assert s.cyan("x") == "\033[36mx\033[0m"
    assert s.dim("x") == "\033[2mx\033[0m"
    assert s.bold_green("x") == "\033[1;32mx\033[0m"
    assert s.bold_red("x") == "\033[1;31mx\033[0m"


def test_no_color_env_disables(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    assert not supports_color()


def test_force_color_env_enables(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert supports_color()


def test_no_color_wins_over_force(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert not supports_color()


def test_supports_color_follows_isatty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)

    class FakeStream:
        def __init__(self, tty: bool) -> None:
            self._tty = tty

        def isatty(self) -> bool:
            return self._tty

    assert supports_color(FakeStream(True))
    assert not supports_color(FakeStream(False))
