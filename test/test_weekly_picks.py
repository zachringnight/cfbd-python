# coding: utf-8

"""
    Test Weekly Picks Generator

    Tests for the weekly college football picks generator example.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add examples directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'examples'))

from weekly_picks import WeeklyPicksGenerator


class TestWeeklyPicksGenerator(unittest.TestCase):
    """Test suite for WeeklyPicksGenerator class."""

    def setUp(self):
        """Set up test fixtures."""
        with patch('cfbd.ApiClient'):
            self.generator = WeeklyPicksGenerator(api_key="test_key")
    
    def test_initialization(self):
        """Test that generator initializes correctly."""
        with patch('cfbd.ApiClient'):
            generator = WeeklyPicksGenerator(api_key="test_key")
            self.assertIsNotNone(generator)
            self.assertIsNotNone(generator.games_api)
            self.assertIsNotNone(generator.betting_api)
            self.assertIsNotNone(generator.ratings_api)
            self.assertIsNotNone(generator.metrics_api)
    
    def test_calculate_pick_confidence_high(self):
        """Test confidence calculation for high confidence pick."""
        confidence, reasoning = self.generator.calculate_pick_confidence(
            ratings_diff=25.0,
            win_prob_diff=40.0,
            spread=-14.0
        )
        self.assertEqual(confidence, "HIGH")
        self.assertIn("Large rating difference", reasoning)
        self.assertIn("Strong win probability edge", reasoning)
    
    def test_calculate_pick_confidence_medium(self):
        """Test confidence calculation for medium confidence pick."""
        confidence, reasoning = self.generator.calculate_pick_confidence(
            ratings_diff=12.0,
            win_prob_diff=18.0,
            spread=None
        )
        self.assertIn(confidence, ["MEDIUM", "HIGH"])
        self.assertIn("rating difference", reasoning)
    
    def test_calculate_pick_confidence_low(self):
        """Test confidence calculation for low confidence pick."""
        confidence, reasoning = self.generator.calculate_pick_confidence(
            ratings_diff=3.0,
            win_prob_diff=5.0,
            spread=None
        )
        self.assertEqual(confidence, "LOW")
    
    def test_make_pick_with_ratings(self):
        """Test making a pick with rating data."""
        # Create mock game
        mock_game = Mock()
        mock_game.id = 12345
        mock_game.home_team = "Alabama"
        mock_game.away_team = "Auburn"
        mock_game.week = 14
        
        # Create mock ratings
        ratings = {
            'elo': {'Alabama': 1850, 'Auburn': 1750},
            'fpi': {'Alabama': 25.5, 'Auburn': 15.3},
            'sp': {'Alabama': 28.0, 'Auburn': 18.5},
            'srs': {'Alabama': 22.1, 'Auburn': 12.8}
        }
        
        # Create mock win probabilities
        win_probs = {
            12345: {
                'home_win_prob': 75.0,
                'away_win_prob': 25.0,
                'spread': -14.0
            }
        }
        
        # Create mock betting data
        betting_data = {
            12345: {
                'spread': -14.0,
                'over_under': 55.5
            }
        }
        
        pick = self.generator.make_pick(mock_game, ratings, win_probs, betting_data)
        
        self.assertEqual(pick['pick'], 'Alabama')
        self.assertEqual(pick['game_id'], 12345)
        self.assertIn(pick['confidence'], ['LOW', 'MEDIUM', 'HIGH'])
        self.assertIsNotNone(pick['reasoning'])
    
    def test_make_pick_without_data(self):
        """Test making a pick with minimal data."""
        mock_game = Mock()
        mock_game.id = 12345
        mock_game.home_team = "Team A"
        mock_game.away_team = "Team B"
        mock_game.week = 5
        
        ratings = {
            'elo': {},
            'fpi': {},
            'sp': {},
            'srs': {}
        }
        
        pick = self.generator.make_pick(mock_game, ratings, {}, {})
        
        # Should default to home team with minimal data
        self.assertEqual(pick['pick'], 'Team A')
        self.assertIsNotNone(pick['confidence'])
    
    def test_make_pick_away_favorite(self):
        """Test making a pick when away team is favored."""
        mock_game = Mock()
        mock_game.id = 12345
        mock_game.home_team = "Underdog"
        mock_game.away_team = "Favorite"
        mock_game.week = 5
        
        ratings = {
            'elo': {'Underdog': 1600, 'Favorite': 1800},
            'fpi': {'Underdog': 10.0, 'Favorite': 25.0},
            'sp': {},
            'srs': {}
        }
        
        win_probs = {
            12345: {
                'home_win_prob': 30.0,
                'away_win_prob': 70.0,
                'spread': 10.0
            }
        }
        
        pick = self.generator.make_pick(mock_game, ratings, win_probs, {})
        
        self.assertEqual(pick['pick'], 'Favorite')
    
    def test_get_weekly_games_error_handling(self):
        """Test error handling when fetching games fails."""
        from cfbd.rest import ApiException
        self.generator.games_api.get_games = Mock(side_effect=ApiException("API Error"))
        
        games = self.generator.get_weekly_games(2023, 5)
        
        self.assertEqual(games, [])
    
    def test_get_betting_lines_error_handling(self):
        """Test error handling when fetching betting lines fails."""
        from cfbd.rest import ApiException
        self.generator.betting_api.get_lines = Mock(side_effect=ApiException("API Error"))
        
        betting_data = self.generator.get_betting_lines(2023, 5)
        
        self.assertEqual(betting_data, {})
    
    def test_print_picks_empty(self):
        """Test printing picks with empty list."""
        # Should not raise an exception
        self.generator.print_picks([])
    
    def test_print_picks_with_data(self):
        """Test printing picks with actual data."""
        picks = [
            {
                'game_id': 1,
                'home_team': 'Home',
                'away_team': 'Away',
                'week': 5,
                'pick': 'Home',
                'confidence': 'HIGH',
                'reasoning': 'Test reasoning',
                'spread': -7.0,
                'win_probability': 65.0
            },
            {
                'game_id': 2,
                'home_team': 'Team A',
                'away_team': 'Team B',
                'week': 5,
                'pick': 'Team B',
                'confidence': 'MEDIUM',
                'reasoning': 'Another reason',
                'spread': 3.5,
                'win_probability': 45.0
            }
        ]
        
        # Should not raise an exception
        self.generator.print_picks(picks, show_reasoning=True)
        self.generator.print_picks(picks, show_reasoning=False)
    
    def test_confidence_filtering(self):
        """Test that confidence filtering works correctly."""
        picks = [
            {'confidence': 'HIGH', 'pick': 'Team1'},
            {'confidence': 'MEDIUM', 'pick': 'Team2'},
            {'confidence': 'LOW', 'pick': 'Team3'},
        ]
        
        high_only = [p for p in picks if ['LOW', 'MEDIUM', 'HIGH'].index(p['confidence']) >= ['LOW', 'MEDIUM', 'HIGH'].index('HIGH')]
        self.assertEqual(len(high_only), 1)
        
        medium_up = [p for p in picks if ['LOW', 'MEDIUM', 'HIGH'].index(p['confidence']) >= ['LOW', 'MEDIUM', 'HIGH'].index('MEDIUM')]
        self.assertEqual(len(medium_up), 2)
        
        all_picks = [p for p in picks if ['LOW', 'MEDIUM', 'HIGH'].index(p['confidence']) >= ['LOW', 'MEDIUM', 'HIGH'].index('LOW')]
        self.assertEqual(len(all_picks), 3)


if __name__ == '__main__':
    unittest.main()
