import random
import secrets
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from rps.bots import make_bot, BUILTIN_BOTS
from rps.game import validate_moves, Score, Round, resolve
from rps.graph import build_rule_graph
from rps.rules import load_rules, list_available_rules

TEMPLATES_DIR = Path(__file__).parent / "templates"
COOKIE = "rps_session"
DEFAULT_RULES = "classic"
DEFAULT_BOT = "random"

app = FastAPI(title="RPS")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


class WebGame:
    def __init__(
        self, rules_name: str, bot_name: str, seed: Optional[int] = None
    ) -> None:
        self.rules_name = rules_name
        self.bot_name = bot_name
        self.rng = random.Random(seed)
        self._rebuild()

    def _rebuild(self) -> None:
        self.rule_graph = build_rule_graph(load_rules(self.rules_name), rng=self.rng)
        validate_moves(self.rule_graph.all_moves(), self.rules_name)
        self.bot = make_bot(self.bot_name, self.rng)
        self.score = Score()
        self.history: list[Round] = []
        self.last: Optional[dict] = None

    def play(self, move: str) -> None:
        if move not in self.rule_graph.all_moves():
            return
        comp = self.bot.choose(self.rule_graph, self.history)
        outcome = resolve(move, comp, self.rule_graph)
        self.score.record(outcome)
        self.history.append((move, comp))
        self.last = {"user": move, "comp": comp, "outcome": outcome}

    def reset(self) -> None:
        self.score = Score()
        self.history = []
        self.last = None

    def apply_settings(self, rules_name: str, bot_name: str) -> None:
        if rules_name == self.rules_name and bot_name == self.bot_name:
            return
        if rules_name not in list_available_rules():
            raise ValueError(f"unknown rule set: {rules_name!r}")
        if bot_name not in BUILTIN_BOTS:
            raise ValueError(f"unknown bot: {bot_name!r}")
        self.rules_name = rules_name
        self.bot_name = bot_name
        self._rebuild()


SESSIONS: dict[str, WebGame] = {}


def _session(request: Request) -> tuple[str, WebGame]:
    sid = request.cookies.get(COOKIE)
    if sid and sid in SESSIONS:
        return sid, SESSIONS[sid]
    sid = secrets.token_urlsafe(16)
    SESSIONS[sid] = WebGame(DEFAULT_RULES, DEFAULT_BOT)
    return sid, SESSIONS[sid]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    sid, game = _session(request)
    response = templates.TemplateResponse(
        request,
        "game.html",
        {
            "game": game,
            "moves": sorted(game.rule_graph.all_moves()),
            "rules_options": list_available_rules(),
            "bots_options": sorted(BUILTIN_BOTS.keys()),
            "history": list(reversed(game.history[-10:])),
            "last": game.last,
        },
    )
    response.set_cookie(COOKIE, sid, httponly=True, samesite="lax")
    return response


@app.post("/play")
async def play(request: Request, move: str = Form(...)) -> RedirectResponse:
    sid = request.cookies.get(COOKIE)
    if sid and sid in SESSIONS:
        SESSIONS[sid].play(move)
    return RedirectResponse("/", status_code=303)


@app.post("/reset")
async def reset(request: Request) -> RedirectResponse:
    sid = request.cookies.get(COOKIE)
    if sid and sid in SESSIONS:
        SESSIONS[sid].reset()
    return RedirectResponse("/", status_code=303)


@app.post("/settings")
async def settings(
    request: Request, rules: str = Form(...), bot: str = Form(...)
) -> RedirectResponse:
    sid = request.cookies.get(COOKIE)
    if sid and sid in SESSIONS:
        try:
            SESSIONS[sid].apply_settings(rules, bot)
        except (ValueError, KeyError, FileNotFoundError):
            pass
    return RedirectResponse("/", status_code=303)


def run() -> None:
    import uvicorn

    uvicorn.run("rps.web.app:app", host="0.0.0.0", port=8000)
