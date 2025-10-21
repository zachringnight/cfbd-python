"""Tools for building tempo-free Elo style prediction models.

This module adds a light-weight analytics layer on top of the generated CFBD
client.  It focuses on providing a production ready Elo engine that can ingest
historical results returned by the API and then generate forward looking win
probabilities, projected spreads, and win total expectations.  The
implementation is dependency free so that it fits naturally inside the auto
generated client package while still providing powerful modelling tools that
can be customised for individual betting strategies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import log
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Tuple,
    Literal,
)

if TYPE_CHECKING:  # pragma: no cover - imported for static analysis only.
    from cfbd.models.game import Game
else:  # pragma: no cover - runtime fallback for type checking helpers.
    Game = Any  # type: ignore[assignment]

GameLocation = Literal["home", "away", "neutral"]


@dataclass(frozen=True)
class GameResult:
    """Light-weight representation of a completed game result.

    The generated `cfbd.models.Game` type contains a large number of fields
    which are extremely useful for downstream analytics.  For modelling Elo we
    only require a minimal subset.  This class provides a convenient bridge so
    that the prediction engine can remain independent from the generated
    pydantic models while still allowing ergonomic conversions.
    """

    season: int
    week: Optional[int]
    date: date
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    neutral_site: bool = False

    @property
    def margin(self) -> int:
        """The scoring margin from the home team's perspective."""

        return self.home_score - self.away_score

    @property
    def winner(self) -> Optional[str]:
        """Name of the winning team or ``None`` in the event of a tie."""

        if self.home_score > self.away_score:
            return self.home_team
        if self.away_score > self.home_score:
            return self.away_team
        return None

    @classmethod
    def from_game(cls, game: "Game") -> "GameResult":
        """Create a :class:`GameResult` from a generated API :class:`Game`.

        Parameters
        ----------
        game:
            Instance returned by :class:`cfbd.api.GamesApi`.  Only a subset of
            the fields are required for the Elo engine, so missing score data is
            gracefully coerced to zero in order to support partially completed
            games (which can be filtered out upstream if desired).
        """

        if not isinstance(game.start_date, datetime):
            # pydantic guarantees datetime instances but user supplied models may
            # pass strings when leveraging `.parse_obj`.  Normalise eagerly so
            # that the dataclass only ever works with :class:`datetime.date`.
            raw_start = str(game.start_date)
            if raw_start.endswith("Z"):
                raw_start = raw_start[:-1] + "+00:00"
            start_dt = datetime.fromisoformat(raw_start)
        else:
            start_dt = game.start_date

        return cls(
            season=game.season,
            week=getattr(game, "week", None),
            date=start_dt.date(),
            home_team=game.home_team,
            away_team=game.away_team,
            home_score=int(game.home_points or 0),
            away_score=int(game.away_points or 0),
            neutral_site=bool(game.neutral_site),
        )


@dataclass(frozen=True)
class ScheduledGame:
    """Representation of a future matchup used for win total projections."""

    opponent: str
    location: GameLocation = "home"

    def __post_init__(self) -> None:
        if self.location not in {"home", "away", "neutral"}:
            raise ValueError(
                "location must be one of 'home', 'away', or 'neutral'"
            )


class EloPredictor:
    """Tempo-free Elo implementation tailored for college football.

    The class provides both retrospective rating estimation and prospective
    prediction utilities.  It combines the traditional Elo formulation with a
    margin-of-victory multiplier, off-season mean reversion, and optional
    pre-season priors so that analysts can blend returning production or power
    ratings sourced from the CFBD API into the update loop.
    """

    #: Default rating assigned to programs that have not played a game yet.
    DEFAULT_RATING = 1500.0

    def __init__(
        self,
        *,
        k_factor: float = 20.0,
        scale: float = 400.0,
        home_field_advantage: float = 55.0,
        regression_weight: float = 0.33,
        regression_target: float = DEFAULT_RATING,
        preseason_ratings: Optional[Mapping[str, float]] = None,
        season_priors: Optional[Mapping[int, Mapping[str, float]]] = None,
        points_per_rating: float = 25.0,
    ) -> None:
        """Create a new Elo predictor.

        Parameters
        ----------
        k_factor:
            Maximum step size for each update.  Higher values lead to more
            reactive ratings at the expense of stability.
        scale:
            Denominator inside the logistic expectation function.  400 mirrors
            chess Elo while lower values create a steeper probability curve.
        home_field_advantage:
            Additional rating boost applied to the home team (in Elo points).
        regression_weight:
            Fraction of a program's rating that regresses to ``regression_target``
            each off-season.  ``0`` disables mean reversion.
        regression_target:
            Long-run rating mean.  By default every team regresses towards
            :data:`DEFAULT_RATING` between seasons.
        preseason_ratings:
            Optional mapping of program -> rating applied before the first
            processed game.  Helpful for seeding blue-blood programs so that the
            opening weeks are less noisy.
        season_priors:
            Optional nested mapping of season -> (program -> rating).  These
            values overwrite the regressed ratings at the beginning of a new
            season which makes it easy to blend third party power ratings or
            returning production metrics.
        points_per_rating:
            Conversion factor used when translating Elo deltas to predicted point
            spreads.  An advantage of ``points_per_rating`` means we expect the
            home team to outscore the visitor by roughly one point.
        """

        self.k_factor = float(k_factor)
        self.scale = float(scale)
        self.home_field_advantage = float(home_field_advantage)
        self.regression_weight = float(regression_weight)
        self.regression_target = float(regression_target)
        self.points_per_rating = float(points_per_rating)
        self._ratings: Dict[str, float] = {}
        self._preseason_ratings = dict(preseason_ratings or {})
        self._season_priors = {
            season: dict(ratings) for season, ratings in (season_priors or {}).items()
        }
        self._season_openers: Dict[int, Dict[str, float]] = {}
        self._fitted = False

    # ------------------------------------------------------------------
    # Helpers for ingesting and normalising data
    # ------------------------------------------------------------------
    def _ensure_team(self, team: str) -> None:
        if team not in self._ratings:
            base_rating = self._preseason_ratings.get(team, self.regression_target)
            self._ratings[team] = float(base_rating)

    def _apply_season_transition(self, season: int) -> None:
        """Handle off-season regression and priors when a new season begins."""

        if not self._ratings:
            priors = self._season_priors.get(season)
            if priors:
                for team, rating in priors.items():
                    self._ratings[team] = float(rating)
                self._season_openers[season] = dict(self._ratings)
            return

        if self.regression_weight:
            for team, rating in list(self._ratings.items()):
                regressed = (
                    (1.0 - self.regression_weight) * rating
                    + self.regression_weight * self.regression_target
                )
                self._ratings[team] = regressed

        for team, rating in self._season_priors.get(season, {}).items():
            self._ratings[team] = float(rating)

        self._season_openers[season] = dict(self._ratings)

    @staticmethod
    def _sort_key(result: GameResult) -> Tuple[int, int, date, str, str]:
        week = result.week if result.week is not None else 0
        return (result.season, week, result.date, result.home_team, result.away_team)

    # ------------------------------------------------------------------
    # Core Elo logic
    # ------------------------------------------------------------------
    def fit(self, games: Iterable[GameResult]) -> "EloPredictor":
        """Fit the predictor using historical game results."""

        self._ratings = dict(self._preseason_ratings)
        self._season_openers.clear()
        self._fitted = False

        ordered_games = sorted(games, key=self._sort_key)
        if not ordered_games:
            self._fitted = True
            return self

        current_season = ordered_games[0].season
        self._apply_season_transition(current_season)

        for game in ordered_games:
            if game.season != current_season:
                current_season = game.season
                self._apply_season_transition(current_season)

            self._ensure_team(game.home_team)
            self._ensure_team(game.away_team)

            self._update_from_result(game)

        self._fitted = True
        return self

    # Update ------------------------------------------------------------
    def _update_from_result(self, game: GameResult) -> None:
        home_rating = self._ratings[game.home_team]
        away_rating = self._ratings[game.away_team]

        rating_diff = home_rating - away_rating
        if not game.neutral_site:
            rating_diff += self.home_field_advantage

        expected_home = self._expected_score_from_diff(rating_diff)
        actual_home = self._actual_score(game.margin)

        mov_multiplier = self._margin_of_victory_multiplier(game.margin, rating_diff)
        delta = self.k_factor * mov_multiplier * (actual_home - expected_home)

        self._ratings[game.home_team] = home_rating + delta
        self._ratings[game.away_team] = away_rating - delta

    def _expected_score_from_diff(self, rating_diff: float) -> float:
        exponent = -rating_diff / self.scale
        return 1.0 / (1.0 + 10.0 ** exponent)

    @staticmethod
    def _actual_score(margin: int) -> float:
        if margin > 0:
            return 1.0
        if margin < 0:
            return 0.0
        return 0.5

    def _margin_of_victory_multiplier(self, margin: int, rating_diff: float) -> float:
        absolute_margin = abs(margin)
        if absolute_margin <= 1:
            return 1.0
        # Smooth the impact of blowouts so that extremely lopsided scores do not
        # dominate the updates.  The formula mirrors FiveThirtyEight's public
        # college football Elo model.
        return log(absolute_margin + 1.0) * (2.2 / ((rating_diff * 0.001) + 2.2))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def ratings(self) -> Dict[str, float]:
        """Return a copy of the current team ratings."""

        if not self._fitted:
            raise RuntimeError("EloPredictor.fit must be called before accessing ratings")
        return dict(self._ratings)

    def season_openers(self, season: int) -> Dict[str, float]:
        """Retrieve the post-regression ratings that opened a given season."""

        return dict(self._season_openers.get(season, {}))

    def predict_win_probability(
        self, home_team: str, away_team: str, *, neutral_site: bool = False
    ) -> float:
        """Predict the probability of the home team winning the matchup."""

        home_rating = self._ratings.get(home_team, self.regression_target)
        away_rating = self._ratings.get(away_team, self.regression_target)
        rating_diff = home_rating - away_rating
        if not neutral_site:
            rating_diff += self.home_field_advantage
        return self._expected_score_from_diff(rating_diff)

    def predict_point_spread(
        self, home_team: str, away_team: str, *, neutral_site: bool = False
    ) -> float:
        """Predict the point spread in favour of the home team."""

        home_rating = self._ratings.get(home_team, self.regression_target)
        away_rating = self._ratings.get(away_team, self.regression_target)
        rating_diff = home_rating - away_rating
        if not neutral_site:
            rating_diff += self.home_field_advantage
        return rating_diff / self.points_per_rating

    def predict_matchup(
        self, team: str, opponent: str, *, location: GameLocation = "home"
    ) -> Tuple[float, float]:
        """Return win probability and spread from ``team``'s perspective."""

        if location == "home":
            win_prob = self.predict_win_probability(team, opponent, neutral_site=False)
            spread = self.predict_point_spread(team, opponent, neutral_site=False)
        elif location == "away":
            home_prob = self.predict_win_probability(opponent, team, neutral_site=False)
            win_prob = 1.0 - home_prob
            spread = -self.predict_point_spread(opponent, team, neutral_site=False)
        elif location == "neutral":
            win_prob = self.predict_win_probability(team, opponent, neutral_site=True)
            spread = self.predict_point_spread(team, opponent, neutral_site=True)
        else:  # pragma: no cover - guarded by ScheduledGame validation.
            raise ValueError("location must be 'home', 'away', or 'neutral'")
        return win_prob, spread

    def expected_wins(self, team: str, schedule: Iterable[ScheduledGame]) -> float:
        """Compute the expected number of wins for a future schedule."""

        total = 0.0
        for matchup in schedule:
            win_prob, _ = self.predict_matchup(team, matchup.opponent, location=matchup.location)
            total += win_prob
        return total

    # Convenience methods -----------------------------------------------
    def iter_rankings(self) -> Iterator[Tuple[str, float]]:
        """Iterate over teams ordered by rating descending."""

        if not self._fitted:
            raise RuntimeError("Call fit() before requesting rankings")
        return iter(sorted(self._ratings.items(), key=lambda item: item[1], reverse=True))

    def top_n(self, n: int = 25) -> List[Tuple[str, float]]:
        """Return the top *n* rated programs."""

        return list(self._safe_take(self.iter_rankings(), n))

    @staticmethod
    def _safe_take(iterator: Iterator[Tuple[str, float]], n: int) -> Iterator[Tuple[str, float]]:
        count = 0
        for item in iterator:
            if count >= n:
                break
            yield item
            count += 1
