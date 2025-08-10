from typing import Optional

from pydantic import BaseModel

from shared_types import Card, CardColor, DrawSource, GameState, PlayTarget


class StartGameResponse(BaseModel):
    state: GameState


class PlayRequest(BaseModel):
    card: Card
    target: PlayTarget
    color: CardColor


class DrawRequest(BaseModel):
    source: DrawSource
    color: Optional[CardColor] = None


class TurnResponse(BaseModel):
    state: GameState
    game_over: bool
    scores: Optional[dict[str, int]] = None
    winner: Optional[str] = None
