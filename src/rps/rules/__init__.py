import tomllib
from importlib.resources import files

_PACKAGE = __package__
_EXT = ".toml"


def list_available_rules() -> list[str]:
    rules_dir = files(_PACKAGE)
    return sorted(
        entry.name.removesuffix(_EXT)
        for entry in rules_dir.iterdir()
        if entry.is_file() and entry.name.endswith(_EXT)
    )


def load_rules(name: str) -> dict[str, list[str]]:
    rules_file = files(_PACKAGE).joinpath(f"{name}{_EXT}")
    with rules_file.open("rb") as f:
        return tomllib.load(f)
