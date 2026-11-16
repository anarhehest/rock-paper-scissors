import pytest

from rules import list_available_rules, load_rules


def test_list_available_rules_returns_sorted_names():
    names = list_available_rules()
    assert names == sorted(names)
    assert len(names) > 0


def test_list_available_rules_contains_known_sets():
    names = list_available_rules()
    assert "classic" in names
    assert "startrek" in names


def test_load_rules_classic():
    rules = load_rules("classic")
    assert rules == {
        "rock": ["scissors"],
        "paper": ["rock"],
        "scissors": ["paper"],
    }


def test_load_rules_startrek():
    rules = load_rules("startrek")
    assert set(rules.keys()) == {"rock", "paper", "scissors", "lizard", "spock"}
    assert rules["spock"] == ["scissors", "rock"]


def test_load_rules_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_rules("nonexistent")


def test_all_rules_are_lowercase():
    for name in list_available_rules():
        rules = load_rules(name)
        for winner, losers in rules.items():
            assert winner == winner.lower(), f"{name}: {winner!r} not lowercase"
            for loser in losers:
                assert loser == loser.lower(), f"{name}: {loser!r} not lowercase"
