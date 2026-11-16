# rock-paper-scissors

A terminal Rock-Paper-Scissors (and friends) game with pluggable rule sets.

## Install

```bash
poetry install
```

## Run

```bash
poetry run rps classic
poetry run rps startrek
poetry run rps classic --first-to 5
poetry run rps classic --bot beat-last
```

## Options

```
RULES                 rule set name (see --help for available sets)
--first-to N          play until either side wins N rounds (default: 1)
--bot NAME            bot to play against (default: random)
--bot-file PATH       load a custom bot from a Python file
--no-color            disable colored output (also honors NO_COLOR)
```

In-game: enter a move, or `q` / `quit` / `exit` to leave.

## Rule sets

Rule sets are TOML files in `src/rps/rules/`, mapping a move to the moves it beats:

```toml
rock     = ["scissors"]
paper    = ["rock"]
scissors = ["paper"]
```

Move names must be lowercase. To add a set, drop a new `.toml` file in that directory.

## Development

```bash
poetry run pytest -v
```

## Requirements

Python 3.13+
