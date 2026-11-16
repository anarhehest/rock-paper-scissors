from main import Score


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
