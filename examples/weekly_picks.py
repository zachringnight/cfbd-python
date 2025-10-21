#!/usr/bin/env python3
"""
Weekly College Football Picks Generator

This script demonstrates how to use the CFBD API to generate weekly college football
game picks based on multiple data sources including:
- Betting lines and spreads
- Team ratings (ELO, SP+, FPI, SRS)
- Pregame win probabilities
- Recent performance metrics
- Advanced team statistics

The script provides recommendations with confidence levels based on data analysis.
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import cfbd
from cfbd.rest import ApiException


class WeeklyPicksGenerator:
    """Generate weekly college football picks using CFBD API data."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the picks generator.
        
        Args:
            api_key: CFBD API key (optional, can be set via CFBD_API_KEY env var)
        """
        configuration = cfbd.Configuration(
            host="https://api.collegefootballdata.com"
        )
        
        # Set API key if provided
        if api_key:
            configuration.access_token = api_key
        elif os.environ.get("CFBD_API_KEY"):
            configuration.access_token = os.environ.get("CFBD_API_KEY")
        
        self.api_client = cfbd.ApiClient(configuration)
        self.games_api = cfbd.GamesApi(self.api_client)
        self.betting_api = cfbd.BettingApi(self.api_client)
        self.ratings_api = cfbd.RatingsApi(self.api_client)
        self.metrics_api = cfbd.MetricsApi(self.api_client)
        self.stats_api = cfbd.StatsApi(self.api_client)
        self.teams_api = cfbd.TeamsApi(self.api_client)
    
    def get_weekly_games(self, year: int, week: int, 
                        season_type: str = "regular",
                        conference: Optional[str] = None) -> List:
        """
        Fetch games for a specific week.
        
        Args:
            year: Season year
            week: Week number
            season_type: Type of season (regular, postseason)
            conference: Optional conference filter
            
        Returns:
            List of games for the specified week
        """
        try:
            games = self.games_api.get_games(
                year=year,
                week=week,
                season_type=season_type,
                conference=conference
            )
            return games
        except ApiException as e:
            print(f"Error fetching games: {e}")
            return []
    
    def get_betting_lines(self, year: int, week: int, 
                         season_type: str = "regular") -> Dict:
        """
        Fetch betting lines for games in a specific week.
        
        Args:
            year: Season year
            week: Week number
            season_type: Type of season
            
        Returns:
            Dictionary mapping game IDs to betting information
        """
        try:
            lines = self.betting_api.get_lines(
                year=year,
                week=week,
                season_type=season_type
            )
            
            betting_data = {}
            for game in lines:
                if game.id:
                    betting_data[game.id] = {
                        'spread': None,
                        'over_under': None,
                        'lines': []
                    }
                    
                    if game.lines:
                        for line in game.lines:
                            betting_data[game.id]['lines'].append({
                                'provider': line.provider,
                                'spread': line.spread,
                                'formatted_spread': line.formatted_spread,
                                'over_under': line.over_under
                            })
                            
                            # Use the first available spread
                            if line.spread and betting_data[game.id]['spread'] is None:
                                betting_data[game.id]['spread'] = line.spread
                            if line.over_under and betting_data[game.id]['over_under'] is None:
                                betting_data[game.id]['over_under'] = line.over_under
            
            return betting_data
        except ApiException as e:
            print(f"Error fetching betting lines: {e}")
            return {}
    
    def get_team_ratings(self, year: int, week: Optional[int] = None) -> Dict:
        """
        Fetch various team ratings for analysis.
        
        Args:
            year: Season year
            week: Optional week filter
            
        Returns:
            Dictionary with team ratings from multiple systems
        """
        ratings = {
            'elo': {},
            'fpi': {},
            'sp': {},
            'srs': {}
        }
        
        try:
            # Get ELO ratings
            elo_ratings = self.ratings_api.get_elo(year=year, week=week)
            for rating in elo_ratings:
                if rating.team:
                    ratings['elo'][rating.team] = rating.elo
            
            # Get FPI ratings
            fpi_ratings = self.ratings_api.get_fpi(year=year)
            for rating in fpi_ratings:
                if rating.team:
                    ratings['fpi'][rating.team] = rating.fpi
            
            # Get SP+ ratings
            sp_ratings = self.ratings_api.get_sp(year=year)
            for rating in sp_ratings:
                if rating.team:
                    ratings['sp'][rating.team] = rating.rating
            
            # Get SRS ratings
            srs_ratings = self.ratings_api.get_srs(year=year)
            for rating in srs_ratings:
                if rating.team:
                    ratings['srs'][rating.team] = rating.rating
            
        except ApiException as e:
            print(f"Warning: Could not fetch all ratings: {e}")
        
        return ratings
    
    def get_win_probabilities(self, year: int, week: int,
                             season_type: str = "regular") -> Dict:
        """
        Fetch pregame win probabilities.
        
        Args:
            year: Season year
            week: Week number
            season_type: Type of season
            
        Returns:
            Dictionary mapping game IDs to win probability data
        """
        try:
            probabilities = self.metrics_api.get_pregame_win_probabilities(
                year=year,
                week=week,
                season_type=season_type
            )
            
            prob_data = {}
            for prob in probabilities:
                if prob.game_id:
                    prob_data[prob.game_id] = {
                        'home_win_prob': prob.home_win_prob,
                        'away_win_prob': prob.away_win_prob,
                        'spread': prob.spread
                    }
            
            return prob_data
        except ApiException as e:
            print(f"Error fetching win probabilities: {e}")
            return {}
    
    def calculate_pick_confidence(self, 
                                 ratings_diff: float,
                                 win_prob_diff: float,
                                 spread: Optional[float]) -> Tuple[str, str]:
        """
        Calculate pick confidence based on available data.
        
        Args:
            ratings_diff: Difference in team ratings
            win_prob_diff: Difference in win probabilities
            spread: Betting spread
            
        Returns:
            Tuple of (confidence_level, reasoning)
        """
        confidence_score = 0
        reasons = []
        
        # Rating difference contributes to confidence
        if abs(ratings_diff) > 20:
            confidence_score += 3
            reasons.append(f"Large rating difference ({ratings_diff:.1f})")
        elif abs(ratings_diff) > 10:
            confidence_score += 2
            reasons.append(f"Moderate rating difference ({ratings_diff:.1f})")
        elif abs(ratings_diff) > 5:
            confidence_score += 1
            reasons.append(f"Small rating difference ({ratings_diff:.1f})")
        
        # Win probability difference
        if abs(win_prob_diff) > 30:
            confidence_score += 3
            reasons.append(f"Strong win probability edge ({win_prob_diff:.1f}%)")
        elif abs(win_prob_diff) > 15:
            confidence_score += 2
            reasons.append(f"Moderate win probability edge ({win_prob_diff:.1f}%)")
        elif abs(win_prob_diff) > 5:
            confidence_score += 1
            reasons.append(f"Slight win probability edge ({win_prob_diff:.1f}%)")
        
        # Spread agreement
        if spread is not None:
            if (ratings_diff > 0 and spread < 0) or (ratings_diff < 0 and spread > 0):
                confidence_score += 2
                reasons.append("Ratings align with spread")
        
        # Determine confidence level
        if confidence_score >= 6:
            confidence = "HIGH"
        elif confidence_score >= 3:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        reasoning = "; ".join(reasons) if reasons else "Limited data available"
        return confidence, reasoning
    
    def make_pick(self, game, ratings: Dict, win_probs: Dict, 
                 betting_data: Dict) -> Dict:
        """
        Generate a pick for a single game.
        
        Args:
            game: Game object from API
            ratings: Team ratings dictionary
            win_probs: Win probabilities dictionary
            betting_data: Betting lines dictionary
            
        Returns:
            Dictionary containing pick information
        """
        pick_data = {
            'game_id': game.id,
            'home_team': game.home_team,
            'away_team': game.away_team,
            'week': game.week,
            'pick': None,
            'confidence': None,
            'reasoning': None,
            'spread': None,
            'win_probability': None
        }
        
        # Get betting information
        if game.id in betting_data:
            pick_data['spread'] = betting_data[game.id].get('spread')
        
        # Calculate average rating for each team
        home_ratings = []
        away_ratings = []
        
        for rating_type in ['elo', 'fpi', 'sp', 'srs']:
            if game.home_team in ratings[rating_type]:
                home_ratings.append(ratings[rating_type][game.home_team])
            if game.away_team in ratings[rating_type]:
                away_ratings.append(ratings[rating_type][game.away_team])
        
        # Calculate rating differences
        ratings_diff = 0
        if home_ratings and away_ratings:
            avg_home = sum(home_ratings) / len(home_ratings)
            avg_away = sum(away_ratings) / len(away_ratings)
            ratings_diff = avg_home - avg_away
        
        # Get win probability data
        win_prob_diff = 0
        if game.id in win_probs:
            home_prob = win_probs[game.id].get('home_win_prob', 50)
            away_prob = win_probs[game.id].get('away_win_prob', 50)
            win_prob_diff = home_prob - away_prob
            pick_data['win_probability'] = home_prob
        
        # Make the pick
        if ratings_diff > 0 or win_prob_diff > 0:
            pick_data['pick'] = game.home_team
        elif ratings_diff < 0 or win_prob_diff < 0:
            pick_data['pick'] = game.away_team
        else:
            # No clear edge, go with home team advantage
            pick_data['pick'] = game.home_team
            ratings_diff = 1  # Small home advantage
        
        # Calculate confidence
        confidence, reasoning = self.calculate_pick_confidence(
            ratings_diff, win_prob_diff, pick_data['spread']
        )
        pick_data['confidence'] = confidence
        pick_data['reasoning'] = reasoning
        
        return pick_data
    
    def generate_weekly_picks(self, year: int, week: int,
                            season_type: str = "regular",
                            conference: Optional[str] = None,
                            min_confidence: Optional[str] = None) -> List[Dict]:
        """
        Generate picks for all games in a week.
        
        Args:
            year: Season year
            week: Week number
            season_type: Type of season (regular, postseason)
            conference: Optional conference filter
            min_confidence: Minimum confidence level to include (HIGH, MEDIUM, LOW)
            
        Returns:
            List of pick dictionaries
        """
        print(f"Generating picks for {year} Week {week} ({season_type})...")
        print("=" * 80)
        
        # Fetch all required data
        print("Fetching games...")
        games = self.get_weekly_games(year, week, season_type, conference)
        if not games:
            print("No games found for specified criteria.")
            return []
        print(f"Found {len(games)} games")
        
        print("Fetching betting lines...")
        betting_data = self.get_betting_lines(year, week, season_type)
        
        print("Fetching team ratings...")
        ratings = self.get_team_ratings(year, week)
        
        print("Fetching win probabilities...")
        win_probs = self.get_win_probabilities(year, week, season_type)
        
        print("\nGenerating picks...")
        print("=" * 80)
        
        # Generate picks for each game
        all_picks = []
        for game in games:
            if game.home_team and game.away_team:
                pick = self.make_pick(game, ratings, win_probs, betting_data)
                
                # Filter by confidence if specified
                if min_confidence:
                    confidence_levels = ['LOW', 'MEDIUM', 'HIGH']
                    if confidence_levels.index(pick['confidence']) >= confidence_levels.index(min_confidence):
                        all_picks.append(pick)
                else:
                    all_picks.append(pick)
        
        return all_picks
    
    def print_picks(self, picks: List[Dict], show_reasoning: bool = True):
        """
        Print picks in a readable format.
        
        Args:
            picks: List of pick dictionaries
            show_reasoning: Whether to show detailed reasoning
        """
        if not picks:
            print("No picks to display.")
            return
        
        # Group by confidence
        high_confidence = [p for p in picks if p['confidence'] == 'HIGH']
        medium_confidence = [p for p in picks if p['confidence'] == 'MEDIUM']
        low_confidence = [p for p in picks if p['confidence'] == 'LOW']
        
        print(f"\n{'=' * 80}")
        print(f"WEEKLY PICKS SUMMARY ({len(picks)} games)")
        print(f"{'=' * 80}")
        print(f"High Confidence: {len(high_confidence)}")
        print(f"Medium Confidence: {len(medium_confidence)}")
        print(f"Low Confidence: {len(low_confidence)}")
        
        for confidence_level, picks_list in [
            ("HIGH CONFIDENCE PICKS", high_confidence),
            ("MEDIUM CONFIDENCE PICKS", medium_confidence),
            ("LOW CONFIDENCE PICKS", low_confidence)
        ]:
            if picks_list:
                print(f"\n{'-' * 80}")
                print(f"{confidence_level}")
                print(f"{'-' * 80}")
                
                for pick in picks_list:
                    print(f"\n{pick['away_team']} @ {pick['home_team']}")
                    print(f"  Pick: {pick['pick']} ({pick['confidence']} confidence)")
                    
                    if pick['spread'] is not None:
                        print(f"  Spread: {pick['spread']}")
                    
                    if pick['win_probability'] is not None:
                        other_prob = 100 - pick['win_probability']
                        if pick['pick'] == pick['home_team']:
                            print(f"  Win Probability: {pick['home_team']} {pick['win_probability']:.1f}% | {pick['away_team']} {other_prob:.1f}%")
                        else:
                            print(f"  Win Probability: {pick['away_team']} {other_prob:.1f}% | {pick['home_team']} {pick['win_probability']:.1f}%")
                    
                    if show_reasoning and pick['reasoning']:
                        print(f"  Reasoning: {pick['reasoning']}")
        
        print(f"\n{'=' * 80}\n")


def main():
    """Main function to demonstrate weekly picks generation."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate weekly college football picks using CFBD API data'
    )
    parser.add_argument('--year', type=int, required=True,
                       help='Season year (e.g., 2023)')
    parser.add_argument('--week', type=int, required=True,
                       help='Week number (e.g., 1)')
    parser.add_argument('--season-type', type=str, default='regular',
                       choices=['regular', 'postseason'],
                       help='Season type (default: regular)')
    parser.add_argument('--conference', type=str,
                       help='Optional conference filter (e.g., SEC, B1G)')
    parser.add_argument('--min-confidence', type=str,
                       choices=['LOW', 'MEDIUM', 'HIGH'],
                       help='Minimum confidence level to display')
    parser.add_argument('--api-key', type=str,
                       help='CFBD API key (or set CFBD_API_KEY env var)')
    parser.add_argument('--no-reasoning', action='store_true',
                       help='Hide detailed reasoning for picks')
    
    args = parser.parse_args()
    
    # Check for API key
    if not args.api_key and not os.environ.get('CFBD_API_KEY'):
        print("Warning: No API key provided. Some endpoints may not work.")
        print("Get an API key from: https://collegefootballdata.com/key")
        print("Set it with --api-key or CFBD_API_KEY environment variable.\n")
    
    try:
        # Initialize generator
        generator = WeeklyPicksGenerator(api_key=args.api_key)
        
        # Generate picks
        picks = generator.generate_weekly_picks(
            year=args.year,
            week=args.week,
            season_type=args.season_type,
            conference=args.conference,
            min_confidence=args.min_confidence
        )
        
        # Display picks
        generator.print_picks(picks, show_reasoning=not args.no_reasoning)
        
        # Summary statistics
        if picks:
            high_conf = sum(1 for p in picks if p['confidence'] == 'HIGH')
            print(f"Generated {len(picks)} picks")
            print(f"Recommended plays: {high_conf} high confidence picks")
        
    except ApiException as e:
        print(f"\nAPI Error: {e}")
        if e.status == 401:
            print("Authentication failed. Check your API key.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
