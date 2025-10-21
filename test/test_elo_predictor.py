from datetime import date, datetime
from types import SimpleNamespace

import pytest

from cfbd.analytics import EloPredictor, GameResult, ScheduledGame


def _sample_games():
    return [
        GameResult(
            season=2022,
            week=1,
            date=date(2022, 9, 1),
            home_team="Alabama",
            away_team="Utah State",
            home_score=55,
            away_score=0,
        ),
        GameResult(
            season=2022,
            week=2,
            date=date(2022, 9, 10),
            home_team="Texas",
            away_team="Alabama",
            home_score=19,
            away_score=20,
        ),
        GameResult(
            season=2022,
            week=7,
            date=date(2022, 10, 15),
            home_team="Tennessee",
            away_team="Alabama",
            home_score=52,
            away_score=49,
        ),
        GameResult(
            season=2023,
            week=1,
            date=date(2023, 9, 2),
            home_team="Alabama",
            away_team="Middle Tennessee",
            home_score=56,
            away_score=7,
        ),
    ]


def test_elo_predictor_rewards_wins():
    predictor = EloPredictor(k_factor=25.0, regression_weight=0.0)
    predictor.fit(_sample_games())

    ratings = predictor.ratings()
    assert ratings["Alabama"] > ratings["Utah State"]
    assert ratings["Alabama"] > ratings["Texas"]


def test_predict_matchup_accounts_for_location():
    predictor = EloPredictor(k_factor=25.0, regression_weight=0.0)
    predictor.fit(_sample_games())

    home_prob = predictor.predict_matchup("Alabama", "Texas", location="home")[0]
    away_prob = predictor.predict_matchup("Alabama", "Texas", location="away")[0]

    assert home_prob > 0.5
    assert away_prob < home_prob


def test_expected_wins_matches_probability_sum():
    predictor = EloPredictor(k_factor=25.0, regression_weight=0.0)
    predictor.fit(_sample_games())

    schedule = [
        ScheduledGame(opponent="Texas", location="home"),
        ScheduledGame(opponent="Tennessee", location="away"),
        ScheduledGame(opponent="Utah State", location="neutral"),
    ]

    expected = sum(
        predictor.predict_matchup("Alabama", g.opponent, location=g.location)[0]
        for g in schedule
    )
    assert predictor.expected_wins("Alabama", schedule) == pytest.approx(expected)


def test_game_result_from_game_handles_pydantic_models():
    game = SimpleNamespace(
        season=2022,
        week=5,
        start_date=datetime(2022, 10, 1, 19, 0),
        home_team="Alabama",
        away_team="Arkansas",
        home_points=49,
        away_points=26,
        neutral_site=False,
    )

    result = GameResult.from_game(game)

    assert result.season == 2022
    assert result.week == 5
    assert result.date == datetime(2022, 10, 1, 19, 0).date()
    assert result.home_team == "Alabama"
    assert result.away_score == 26


def test_season_regression_resets_ratings():
    predictor = EloPredictor(k_factor=25.0, regression_weight=1.0)
    predictor.fit(_sample_games())

    openers = predictor.season_openers(2023)
    assert openers["Alabama"] == pytest.approx(EloPredictor.DEFAULT_RATING)
