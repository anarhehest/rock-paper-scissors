import pytest
import random

from src.rps.graph import RuleGraph, build_rule_graph

CLASSIC = {"rock": ["scissors"], "paper": ["rock"], "scissors": ["paper"]}


def test_add_move_creates_empty_node():
    g = RuleGraph()
    g.add_move("rock")
    assert "rock" in g.graph
    assert g.graph["rock"] == set()


def test_add_move_is_idempotent():
    g = RuleGraph()
    g.add_move("rock")
    g.add_move("rock")
    assert g.all_moves() == {"rock"}


def test_add_rule_creates_edge_and_nodes():
    g = RuleGraph()
    g.add_rule("rock", "scissors")
    assert g.does_beat("rock", "scissors")
    assert not g.does_beat("scissors", "rock")
    assert g.all_moves() == {"rock", "scissors"}


def test_add_rule_self_loop_raises():
    g = RuleGraph()
    with pytest.raises(ValueError, match="cannot beat itself"):
        g.add_rule("rock", "rock")


def test_does_beat_unknown_move_returns_false():
    g = RuleGraph()
    g.add_rule("rock", "scissors")
    assert not g.does_beat("banana", "scissors")
    assert not g.does_beat("rock", "banana")


def test_empty_graph_get_random_move_raises():
    g = RuleGraph()
    with pytest.raises(ValueError, match="empty"):
        g.get_random_move()


def test_get_random_move_returns_member():
    g = RuleGraph()
    g.add_rule("rock", "scissors")
    g.add_rule("paper", "rock")
    moves = g.all_moves()
    for _ in range(50):
        assert g.get_random_move() in moves


def test_all_moves_returns_new_set():
    g = RuleGraph()
    g.add_move("rock")
    s = g.all_moves()
    s.add("dragon")
    assert "dragon" not in g.all_moves()


def test_build_rule_graph_from_dict():
    g = build_rule_graph({"rock": ["scissors"], "paper": ["rock"]})
    assert g.all_moves() == {"rock", "paper", "scissors"}
    assert g.does_beat("rock", "scissors")
    assert g.does_beat("paper", "rock")
    assert not g.does_beat("scissors", "paper")


def test_build_rule_graph_empty():
    g = build_rule_graph({})
    assert g.all_moves() == set()
    with pytest.raises(ValueError):
        g.get_random_move()


def test_build_rule_graph_rejects_self_loop():
    with pytest.raises(ValueError, match="cannot beat itself"):
        build_rule_graph({"rock": ["rock"]})


def test_rule_graph_with_seed_is_deterministic():
    g1 = build_rule_graph(CLASSIC, rng=random.Random(42))
    g2 = build_rule_graph(CLASSIC, rng=random.Random(42))
    seq1 = [g1.get_random_move() for _ in range(10)]
    seq2 = [g2.get_random_move() for _ in range(10)]
    assert seq1 == seq2


def test_rule_graph_different_seeds_differ():
    g1 = build_rule_graph(CLASSIC, rng=random.Random(1))
    g2 = build_rule_graph(CLASSIC, rng=random.Random(2))
    seq1 = [g1.get_random_move() for _ in range(20)]
    seq2 = [g2.get_random_move() for _ in range(20)]
    assert seq1 != seq2