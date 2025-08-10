from __future__ import annotations

import socket
import threading
import time

import pytest
import uvicorn

from domains.game import service
from main import app  # type: ignore[attr-defined]
from shared_types import COLORS, Card, GameState, Stack


@pytest.fixture
def game_state():
    # Use a fixed seed for reproducibility
    return service.init_game(seed=42)


@pytest.fixture
def player1(game_state: GameState):
    return game_state.players[0]


@pytest.fixture
def player2(game_state: GameState):
    return game_state.players[1]


def make_card(color: str, value: int) -> Card:
    return Card(color=color, value=value)  # type: ignore[arg-type]


@pytest.fixture
def sample_expedition():
    st = Stack()
    st.items.extend(
        [
            make_card(COLORS[0], 0),
            make_card(COLORS[0], 0),
            make_card(COLORS[0], 2),
            make_card(COLORS[0], 5),
        ]
    )
    return st


# Automatically run a uvicorn server for end-to-end tests
@pytest.fixture(scope="session", autouse=True)
def uvicorn_server():
    """Boot a live uvicorn server for E2E tests.

    Runs in a background thread and waits for the port to accept connections.
    Shuts down cleanly after the test session completes.
    """
    config = uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for the server socket to accept connections
    for _ in range(200):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", 8001)) == 0:
                break
        time.sleep(0.05)

    yield

    server.should_exit = True
    thread.join(timeout=5)
