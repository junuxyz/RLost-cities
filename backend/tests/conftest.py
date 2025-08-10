from __future__ import annotations

import pytest

from domains.game import service
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
