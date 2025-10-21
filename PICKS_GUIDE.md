# Weekly College Football Picks Generator

## Overview

The Weekly Picks Generator is a comprehensive tool that uses the College Football Data (CFBD) API to generate informed weekly game picks. It analyzes multiple data sources to provide recommendations with confidence levels.

## Features

- **Multi-Source Analysis**: Combines data from betting lines, team ratings (ELO, SP+, FPI, SRS), win probabilities, and advanced metrics
- **Confidence Scoring**: Each pick is assigned a confidence level (HIGH, MEDIUM, LOW) based on data strength
- **Detailed Reasoning**: Provides transparent explanations for each pick
- **Flexible Filtering**: Filter by conference, week, season type, and minimum confidence level
- **Command-Line and Programmatic Usage**: Use as a standalone CLI tool or integrate into your own scripts

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/zachringnight/cfbd-python.git
cd cfbd-python

# Install dependencies
pip install -e .
```

### Get an API Key

Sign up for a free API key at [CollegeFootballData.com](https://collegefootballdata.com/key).

### Basic Usage

```bash
# Set your API key
export CFBD_API_KEY='your-api-key-here'

# Generate picks for a specific week
python examples/weekly_picks.py --year 2023 --week 5

# Filter by conference
python examples/weekly_picks.py --year 2023 --week 5 --conference SEC

# Show only high confidence picks
python examples/weekly_picks.py --year 2023 --week 5 --min-confidence HIGH
```

## Command-Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `--year` | Season year (e.g., 2023) | Yes |
| `--week` | Week number (e.g., 5) | Yes |
| `--season-type` | Season type: `regular` or `postseason` | No (default: regular) |
| `--conference` | Conference abbreviation (e.g., SEC, B1G, ACC) | No |
| `--min-confidence` | Minimum confidence: `LOW`, `MEDIUM`, or `HIGH` | No |
| `--api-key` | CFBD API key | No (uses CFBD_API_KEY env var) |
| `--no-reasoning` | Hide detailed reasoning | No |

## How It Works

### Data Sources

The picks generator analyzes:

1. **Betting Lines**: Point spreads and over/under totals from multiple sportsbooks
2. **Team Ratings**:
   - **ELO**: Chess-style rating system tracking team performance over time
   - **SP+**: Tempo-free ratings adjusting for opponent strength
   - **FPI**: ESPN's Football Power Index
   - **SRS**: Simple Rating System based on point differential and strength of schedule
3. **Win Probabilities**: Pregame win probability models
4. **Advanced Metrics**: Team statistics, performance trends, and efficiency metrics

### Confidence Scoring Algorithm

Confidence levels are calculated based on:

- **Rating Differential**: How much better one team is rated across multiple systems
- **Win Probability Edge**: The predicted win probability advantage
- **Market Agreement**: Whether ratings align with betting market expectations
- **Data Quality**: How much reliable data is available for the matchup

#### Scoring Breakdown:

- **HIGH Confidence (6+ points)**:
  - Large rating differences (>20 points)
  - Strong win probability edges (>30%)
  - Multiple data sources in agreement
  
- **MEDIUM Confidence (3-5 points)**:
  - Moderate rating differences (10-20 points)
  - Moderate win probability edges (15-30%)
  - Some data agreement
  
- **LOW Confidence (0-2 points)**:
  - Small rating differences (<10 points)
  - Slight win probability edges (<15%)
  - Limited or conflicting data

## Output Format

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

Texas A&M @ Alabama
  Pick: Alabama (HIGH confidence)
  Spread: -14.0
  Win Probability: Alabama 82.1% | Texas A&M 17.9%
  Reasoning: Large rating difference (22.4); Strong win probability edge (64.2%); Ratings align with spread
...
```

## Programmatic Usage

You can also use the picks generator in your own Python scripts:

```python
from weekly_picks import WeeklyPicksGenerator

# Initialize with API key
generator = WeeklyPicksGenerator(api_key='your-key-here')

# Generate picks
picks = generator.generate_weekly_picks(
    year=2023,
    week=5,
    season_type='regular',
    conference='SEC',
    min_confidence='MEDIUM'
)

# Display results
generator.print_picks(picks, show_reasoning=True)

# Or process picks programmatically
for pick in picks:
    if pick['confidence'] == 'HIGH':
        print(f"Recommended: {pick['pick']} over {pick['away_team'] if pick['pick'] == pick['home_team'] else pick['home_team']}")
```

## Examples

### Example 1: Conference Championship Week

```bash
python examples/weekly_picks.py --year 2023 --week 14 --min-confidence HIGH
```

Get high-confidence picks for rivalry week games.

### Example 2: Playoff Selection Week

```bash
python examples/weekly_picks.py --year 2023 --week 15 --conference SEC
```

Focus on SEC championship and top-tier matchups.

### Example 3: Bowl Season

```bash
python examples/weekly_picks.py --year 2023 --week 1 --season-type postseason
```

Generate picks for bowl games.

## Testing

The picks generator includes comprehensive tests:

```bash
# Run all tests
python -m pytest test/test_weekly_picks.py -v

# Run specific test
python -m pytest test/test_weekly_picks.py::TestWeeklyPicksGenerator::test_calculate_pick_confidence_high -v
```

## Limitations

- **API Key Required**: Most endpoints require a valid CFBD API key
- **Data Availability**: Some metrics may not be available for all games/teams
- **Historical Data**: Picks are generated based on data available at game time
- **No Guarantees**: This is an analytical tool; actual game outcomes may vary

## Best Practices

1. **Use Multiple Weeks**: Track picks over multiple weeks to understand performance
2. **Combine with Research**: Use picks as one input alongside your own analysis
3. **High Confidence Focus**: Start with high-confidence picks for better results
4. **Conference Filtering**: Focus on conferences you're familiar with
5. **Check Data Freshness**: Ensure you're using current week data

## Troubleshooting

### API Authentication Errors

```
✗ API Exception: 401
```

**Solution**: Verify your API key is correct and properly set:
```bash
export CFBD_API_KEY='your-actual-key'
```

### No Picks Generated

```
No games found for specified criteria.
```

**Solution**: Check that:
- The year/week combination is valid
- Games exist for the specified filters (conference, season type)
- The season has started (week 0 or later)

### Missing Data Warnings

```
Warning: Could not fetch all ratings
```

**Solution**: This is normal when some data sources are unavailable. Picks will still be generated with available data.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Acknowledgments

- [College Football Data API](https://collegefootballdata.com) for providing comprehensive college football data
- The college football analytics community for methodology and insights

## Support

For questions or issues:
- Open an issue on [GitHub](https://github.com/zachringnight/cfbd-python/issues)
- Consult the [API documentation](https://api.collegefootballdata.com/api/docs/)
- Visit the [CFBD website](https://collegefootballdata.com)
