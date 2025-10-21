"""Example demonstrating the analytics.EloPredictor helper."""

from datetime import date

from cfbd.analytics import EloPredictor, GameResult, ScheduledGame


HISTORICAL_RESULTS = [
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

UPCOMING_SCHEDULE = [
    ScheduledGame(opponent="Texas", location="home"),
    ScheduledGame(opponent="Tennessee", location="away"),
    ScheduledGame(opponent="Utah State", location="neutral"),
]


def main() -> None:
    predictor = EloPredictor(k_factor=25.0, regression_weight=0.2)
    predictor.fit(HISTORICAL_RESULTS)

    print("Top teams:")
    for team, rating in predictor.top_n(3):
        print(f"  {team}: {rating:.1f}")

    win_prob, spread = predictor.predict_matchup("Alabama", "Texas", location="home")
    print(f"\nAlabama vs Texas (Tuscaloosa) win probability: {win_prob:.3f}, spread: {spread:.1f}")

    expected = predictor.expected_wins("Alabama", UPCOMING_SCHEDULE)
    print(f"Expected wins across the upcoming schedule: {expected:.2f}")


if __name__ == "__main__":
    main()
