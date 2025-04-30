# Tournament Test Fixtures

This directory contains fixtures for testing tournament workflows in the ChiGame.

## Simulation Test Tournament

`tournaments-simulation-fixture.json` contains a complete tournament setup with the following characteristics:

- **Tournament Details**:
  - Name: Simulation Test Tournament
  - Game: test_game (Game ID: 1)
  - Registration Period: April 1, 2025 - April 20, 2025
  - Tournament Period: April 24, 2025 - May 31, 2025
  - Maximum Players: 8
  - Number of Winners: 1

- **Players**:
  - 8 test players (User IDs: 101-108)
  - All players have emails in the format player#@example.com
  - All players have the password "test"

- **Matches**:
  - 4 quarter-final matches are set up
  - Each match has 2 players assigned
  - All matches are in the initial state (no outcomes yet)

## How to Use These Fixtures

### Loading the Fixtures

```bash
# First load the test players
python manage.py loaddata src/chigame/users/fixtures/test_players.json

# Then load the tournament fixture
python manage.py loaddata src/chigame/games/fixtures/tournaments-simulation-fixture.json
```

### Fixture Structure

The fixture includes:
- Tournament object
- Tournament chat
- Match lobbies
- Match objects
- Player assignments

## Notes for Developers

- All object IDs start from 1001 to avoid conflicts with existing data
- The tournament is set up with test_game (Game ID: 1)
- The tournament is already in the "tournament in progress" state
- This fixture can be used as a starting point for testing different tournament formats:
  - Single elimination (current setup)
  - Double elimination
  - Round robin
  - Multi-Stage
- Test players have IDs 101-108 to avoid conflicts with existing user IDs
