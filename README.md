# rock-paper-scissors

A terminal Rock-Paper-Scissors (and friends) game with pluggable rule sets
and pluggable bots.

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
poetry run rps classic --pvp
poetry run rps classic --seed 42
```

## Options

```
RULES                 rule set name (see --help for available sets)
--first-to N          play until either side wins N rounds (default: 1)
--seed N              seed for reproducible runs (no effect in --pvp)
--bot NAME            bot to play against (default: random)
--bot-file PATH       load a custom bot from a Python file
--pvp                 two-player hot-seat mode
--no-color            disable colored output (also honors NO_COLOR)
```

In-game: enter a move, or `q` / `quit` / `exit` to leave.

## Reproducible runs

`--seed N` fixes the random stream for the whole run, so the same seed
gives the same sequence of computer moves:

```bash
rps classic --seed 42
```

Useful for recording examples, debugging, and writing tests that don't
flake. In `--pvp` there's no randomness, so the flag is a no-op.


## Rule sets

Rule sets are TOML files in `src/rps/rules/`, mapping a move to the moves it beats:

```toml
rock     = ["scissors"]
paper    = ["rock"]
scissors = ["paper"]
```

Move names must be lowercase. To add a set, drop a new `.toml` file in that directory.

## Bots

Built-in bots:

- random — picks a move uniformly at random (default).
- beat-last — plays whatever beats your previous move.

```bash
poetry run rps classic --bot beat-last
```

Custom bots are Python files exposing a `BOT` instance with a `name` and a
`choose(rule_graph, history)` method. `history` is a list of
`(user_move, bot_move)` pairs from previous rounds, most recent last.

```python
# my_bot.py
class MirrorBot:
    name = "mirror"

    def choose(self, rule_graph, history):
        if not history:
            return rule_graph.get_random_move()
        return history[-1][0]

BOT = MirrorBot()
```
```bash
poetry run rps classic --bot-file my_bot.py
```

## Two-player mode (hot-seat)

```bash
poetry run rps classic --pvp
poetry run rps classic --pvp --first-to 3
```

Both players enter moves at the same terminal. Input is hidden via
`getpass` when the terminal supports it; in pipes/redirects it falls
back to plain `input()`.


## Development

```bash
poetry run pytest -v
```

## Requirements

Python 3.13+
