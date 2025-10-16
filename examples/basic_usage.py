#!/usr/bin/env python3
"""
Basic usage example for cfbd Python package.

This example demonstrates how to set up and use the College Football Data API client.
"""

import os
import cfbd
from cfbd.rest import ApiException

def main():
    # Configure API client
    # You can get your API key from https://collegefootballdata.com/key
    configuration = cfbd.Configuration(
        host="https://api.collegefootballdata.com"
    )
    
    # If you have an API key, you can set it like this:
    # configuration.access_token = os.environ.get("CFBD_API_KEY")
    
    # Create API client
    with cfbd.ApiClient(configuration) as api_client:
        # Create API instances
        conferences_api = cfbd.ConferencesApi(api_client)
        teams_api = cfbd.TeamsApi(api_client)
        games_api = cfbd.GamesApi(api_client)
        
        print("CFBD Python Client Example")
        print("=" * 50)
        
        try:
            # Example 1: Get list of conferences
            print("\n1. Fetching conferences...")
            conferences = conferences_api.get_conferences()
            print(f"   Found {len(conferences)} conferences")
            if conferences:
                print(f"   First conference: {conferences[0].name}")
            
            # Example 2: Get FBS teams
            print("\n2. Fetching FBS teams...")
            teams = teams_api.get_fbs_teams(year=2023)
            print(f"   Found {len(teams)} FBS teams for 2023")
            if teams:
                print(f"   First team: {teams[0].school}")
            
            # Example 3: Get games for a specific year and week
            print("\n3. Fetching games...")
            games = games_api.get_games(year=2023, week=1, season_type="regular")
            print(f"   Found {len(games)} games in week 1 of 2023")
            if games:
                game = games[0]
                print(f"   First game: {game.home_team} vs {game.away_team}")
            
            print("\n" + "=" * 50)
            print("✓ All API calls completed successfully!")
            print("\nNote: Some endpoints may require authentication.")
            print("Set CFBD_API_KEY environment variable with your API key.")
            
        except ApiException as e:
            print(f"\n✗ API Exception: {e}")
            if e.status == 401:
                print("   You may need an API key for this endpoint.")
                print("   Get one from: https://collegefootballdata.com/key")

if __name__ == "__main__":
    main()
