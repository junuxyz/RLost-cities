from fastapi import FastAPI

from domains.game.routes import router as game_router

app = FastAPI(title="RLost-Cities Backend")

app.include_router(game_router)
