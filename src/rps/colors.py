import os
import sys
from typing import Optional, TextIO

RESET = "0"
BOLD = "1"
DIM = "2"
RED = "31"
GREEN = "32"
YELLOW = "33"
CYAN = "36"


def supports_color(stream: Optional[TextIO] = None) -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    stream = stream if stream is not None else sys.stdout
    return stream.isatty()


class Style:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, codes: str, text: str) -> str:
        if not self.enabled:
            return text
        return f"\033[{codes}m{text}\033[{RESET}m"

    def green(self, text: str) -> str:
        return self._wrap(GREEN, text)

    def red(self, text: str) -> str:
        return self._wrap(RED, text)

    def yellow(self, text: str) -> str:
        return self._wrap(YELLOW, text)

    def cyan(self, text: str) -> str:
        return self._wrap(CYAN, text)

    def dim(self, text: str) -> str:
        return self._wrap(DIM, text)

    def bold_green(self, text: str) -> str:
        return self._wrap(f"{BOLD};{GREEN}", text)

    def bold_red(self, text: str) -> str:
        return self._wrap(f"{BOLD};{RED}", text)
