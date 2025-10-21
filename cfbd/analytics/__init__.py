"""Predictive analytics utilities built on top of the CFBD API client."""

from .elo import GameResult, ScheduledGame, EloPredictor

__all__ = [
    "GameResult",
    "ScheduledGame",
    "EloPredictor",
]
