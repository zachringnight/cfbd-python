#!/usr/bin/env python3
"""
Demo script showing how to use the WeeklyPicksGenerator programmatically.

This demonstrates how to integrate the picks generator into your own scripts.
"""

import os
import sys

# Add examples directory to path to import weekly_picks
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'examples'))

from weekly_picks import WeeklyPicksGenerator


def main():
    """Demonstrate programmatic usage of the picks generator."""
    
    print("Weekly Picks Generator - Programmatic Usage Demo")
    print("=" * 80)
    
    # Initialize the generator
    # Note: In a real scenario, you would provide an API key
    generator = WeeklyPicksGenerator()
    
    print("\n1. Testing confidence calculation...")
    confidence, reasoning = generator.calculate_pick_confidence(
        ratings_diff=20.5,
        win_prob_diff=35.0,
        spread=-12.5
    )
    print(f"   Sample pick confidence: {confidence}")
    print(f"   Reasoning: {reasoning}")
    
    print("\n2. Creating a sample pick...")
    from unittest.mock import Mock
    
    # Create a mock game
    mock_game = Mock()
    mock_game.id = 12345
    mock_game.home_team = "Alabama"
    mock_game.away_team = "Auburn"
    mock_game.week = 14
    
    # Sample ratings data
    ratings = {
        'elo': {'Alabama': 1900, 'Auburn': 1750},
        'fpi': {'Alabama': 30.5, 'Auburn': 18.3},
        'sp': {'Alabama': 32.0, 'Auburn': 20.5},
        'srs': {'Alabama': 25.1, 'Auburn': 15.8}
    }
    
    # Sample win probabilities
    win_probs = {
        12345: {
            'home_win_prob': 78.0,
            'away_win_prob': 22.0,
            'spread': -14.0
        }
    }
    
    # Sample betting data
    betting_data = {
        12345: {
            'spread': -14.0,
            'over_under': 52.5
        }
    }
    
    pick = generator.make_pick(mock_game, ratings, win_probs, betting_data)
    
    print(f"   Matchup: {pick['away_team']} @ {pick['home_team']}")
    print(f"   Pick: {pick['pick']}")
    print(f"   Confidence: {pick['confidence']}")
    print(f"   Reasoning: {pick['reasoning']}")
    
    print("\n3. Usage with real API:")
    print("   To use with the actual CFBD API, you need an API key:")
    print("   - Get a key from: https://collegefootballdata.com/key")
    print("   - Set it via environment variable: export CFBD_API_KEY='your-key'")
    print("   - Or pass it directly: WeeklyPicksGenerator(api_key='your-key')")
    print("\n   Then you can generate picks like this:")
    print("   ```python")
    print("   generator = WeeklyPicksGenerator(api_key='your-key')")
    print("   picks = generator.generate_weekly_picks(year=2023, week=5)")
    print("   generator.print_picks(picks)")
    print("   ```")
    
    print("\n" + "=" * 80)
    print("Demo complete!")
    print("\nFor command-line usage, run:")
    print("  python examples/weekly_picks.py --year 2023 --week 5 --api-key YOUR_KEY")


if __name__ == "__main__":
    main()
