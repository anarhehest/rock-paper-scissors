import pytest

from rps.bots import BUILTIN_BOTS, BeatLastBot, RandomBot, load_bot_file
from rps.graph import build_rule_graph

CLASSIC = {"rock": ["scissors"], "paper": ["rock"], "scissors": ["paper"]}


@pytest.fixture
def graph():
    return build_rule_graph(CLASSIC)


def test_registry_contains_builtin_bots():
    assert "random" in BUILTIN_BOTS
    assert "beat-last" in BUILTIN_BOTS


def test_random_bot_returns_valid_move(graph):
    bot = RandomBot()
    for _ in range(20):
        assert bot.choose(graph, []) in graph.all_moves()


def test_beat_last_empty_history_returns_valid_move(graph):
    assert BeatLastBot().choose(graph, []) in graph.all_moves()


@pytest.mark.parametrize(
    "user_move,expected",
    [("rock", "paper"), ("paper", "scissors"), ("scissors", "rock")],
)
def test_beat_last_beats_user_move(graph, user_move, expected):
    assert BeatLastBot().choose(graph, [(user_move, "rock")]) == expected


def test_load_bot_file(tmp_path):
    f = tmp_path / "always_rock.py"
    f.write_text(
        "class Bot:\n"
        "    name = 'always-rock'\n"
        "    def choose(self, rule_graph, history):\n"
        "        return 'rock'\n"
        "BOT = Bot()\n"
    )
    bot = load_bot_file(f)
    assert bot.name == "always-rock"


def test_load_bot_file_missing_bot(tmp_path):
    f = tmp_path / "empty.py"
    f.write_text("")
    with pytest.raises(ValueError, match="missing BOT"):
        load_bot_file(f)


def test_load_bot_file_bad_bot(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("BOT = 'not a bot'\n")
    with pytest.raises(ValueError, match="must have"):
        load_bot_file(f)


def test_load_bot_file_not_found(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        load_bot_file(tmp_path / "nope.py")
