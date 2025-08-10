from fastapi import APIRouter, HTTPException

from shared_types import GameState

from .models import DrawRequest, PlayRequest, StartGameResponse, TurnResponse
from .service import init_game, turn

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/start", response_model=StartGameResponse)
def start_game():
    try:
        state = init_game()
        return {"state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/turn", response_model=TurnResponse)
def perform_turn(state: GameState, play: PlayRequest, draw: DrawRequest):
    try:
        current_player = state.players[state.current_player]
        # Execute the full turn (play/discard then draw)
        turn(
            state,
            current_player,
            play.card,
            play.target,
            play.color,
            draw.source,
            draw.color,
        )
        # Build response with game-over metadata for client loops
        if state.phase == "GAME_OVER":
            p1, p2 = state.players
            scores = {"player1": p1.score, "player2": p2.score}
            # Winner naming: "player1", "player2", or "Draw"
            if p1.score > p2.score:
                winner = "player1"
            elif p2.score > p1.score:
                winner = "player2"
            else:
                winner = "Draw"
            return {"state": state, "game_over": True, "scores": scores, "winner": winner}
        return {"state": state, "game_over": False}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
