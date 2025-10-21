# Examples

This directory contains example scripts demonstrating how to use the cfbd Python package.

## Available Examples

### basic_usage.py

A basic example showing how to:
- Configure the API client
- Set up authentication (optional)
- Make API calls to fetch conferences, teams, and games
- Handle API exceptions

To run this example:

```bash
python examples/basic_usage.py
```

If you have an API key, you can set it as an environment variable:

```bash
export CFBD_API_KEY='your-api-key-here'
python examples/basic_usage.py
```

You can get your API key from [CollegeFootballData.com](https://collegefootballdata.com/key).

### weekly_picks.py

A comprehensive tool for generating weekly college football picks using multiple data sources:
- Betting lines and spreads
- Team ratings (ELO, SP+, FPI, SRS)
- Pregame win probabilities
- Advanced analytics and metrics

This script analyzes games and provides recommendations with confidence levels (HIGH, MEDIUM, LOW) based on:
- Rating differentials between teams
- Win probability analysis
- Alignment with betting markets
- Historical performance metrics

**Usage:**

```bash
# Generate picks for a specific week
python examples/weekly_picks.py --year 2023 --week 5

# Filter by conference
python examples/weekly_picks.py --year 2023 --week 5 --conference SEC

# Show only high confidence picks
python examples/weekly_picks.py --year 2023 --week 5 --min-confidence HIGH

# Postseason games
python examples/weekly_picks.py --year 2023 --week 1 --season-type postseason

# With API key
export CFBD_API_KEY='your-api-key-here'
python examples/weekly_picks.py --year 2023 --week 5
```

**Command-line options:**

- `--year YEAR` (required): Season year (e.g., 2023)
- `--week WEEK` (required): Week number (e.g., 5)
- `--season-type {regular,postseason}`: Season type (default: regular)
- `--conference CONF`: Filter by conference abbreviation (e.g., SEC, B1G, ACC)
- `--min-confidence {LOW,MEDIUM,HIGH}`: Show only picks meeting minimum confidence level
- `--api-key KEY`: CFBD API key (or set CFBD_API_KEY environment variable)
- `--no-reasoning`: Hide detailed reasoning for each pick

**Output:**

The tool generates a comprehensive report including:
- Summary of picks by confidence level
- Matchup details with away team @ home team
- Pick recommendation with confidence level
- Betting spread information (when available)
- Win probability percentages
- Detailed reasoning for each pick (ratings differences, probability edges, etc.)

**Example output:**

```
================================================================================
WEEKLY PICKS SUMMARY (15 games)
================================================================================
High Confidence: 5
Medium Confidence: 7
Low Confidence: 3

--------------------------------------------------------------------------------
HIGH CONFIDENCE PICKS
--------------------------------------------------------------------------------

Florida State @ Clemson
  Pick: Clemson (HIGH confidence)
  Spread: -10.5
  Win Probability: Clemson 75.3% | Florida State 24.7%
  Reasoning: Large rating difference (15.2); Strong win probability edge (50.6%); Ratings align with spread

...
```

**Note:** An API key is required for most endpoints. Get yours from [CollegeFootballData.com](https://collegefootballdata.com/key).

## More Examples

For more detailed examples and API documentation, see:
- [Main README](../README.md)
- [API Documentation](../docs/)
