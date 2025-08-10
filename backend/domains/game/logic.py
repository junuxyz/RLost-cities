from __future__ import annotations

import random
from collections import deque
from typing import cast

from backend.shared_types import (
    COLORS,
    Card,
    CardColor,
    CardValue,
    DrawSource,
    Player,
    PlayTarget,
    Stack,
)

# 1. Initialize Game

## Initialize Deck
### Build full deck: per color -> 3 handshake (0) + numbers 2-10
_raw_deck: list[Card] = []
for c in COLORS:
    for _ in range(3):
        _raw_deck.append(Card(color=c, value=0))
    for v in range(2, 11):
        _raw_deck.append(Card(color=c, value=cast(CardValue, v)))
random.shuffle(_raw_deck)
# Convert to deque (top of deck = left side for efficient popleft)
deck: deque[Card] = deque(_raw_deck)


## Initialize Player

player1 = Player()
player2 = Player()

### deal 8 cards to each player (preserving shuffled order) Total card becomes 56.
for _ in range(8):
    player1.hand.append(deck.popleft())
    player2.hand.append(deck.popleft())

# Discard piles: one stack per color (top = end of list)
discard_piles = {c: Stack() for c in COLORS}

# 2. During Game


## Placing (playing or discarding) a card
def put(card: Card, player: Player, target: PlayTarget, color: CardColor) -> None:
    """
    Place a card from player's hand either onto an expedition or a discard pile.
    color indicates which expedition or discard pile.
    """
    if card not in player.hand:
        raise ValueError("Player does not have that card")

    if target == "discard":
        discard_piles[color].items.append(card)
        player.hand.remove(card)
        return

    if target == "expedition":
        stack = player.expeditions[color].items
        last_numbers = [c.value for c in stack if c.value != 0]
        if last_numbers and card.value < last_numbers[-1]:
            raise ValueError("Number card must be >= previous number card")
        stack.append(card)
        player.hand.remove(card)
        return

    raise ValueError("Invalid target for put")


## Drawing a card
def draw(player: Player, source: DrawSource, color: CardColor | None = None) -> Card:
    """
    Draw a card for player from deck or a specific discard pile.
    If drawing from discard, a color must be provided.
    Returns the drawn card.
    """
    if source == "deck":
        if not deck:
            raise ValueError("Deck is empty")
        card = deck.popleft()
        player.hand.append(card)
        return card
    elif source == "discard":
        if color is None:
            raise ValueError("Color required when drawing from discard")
        pile = discard_piles[color].items
        if not pile:
            raise ValueError(f"Discard pile {color} is empty")
        card = pile.pop()  # LIFO
        player.hand.append(card)
        return card
    else:
        raise ValueError("Invalid draw source")


def turn(
    player: Player,
    play_card: Card,
    play_target: PlayTarget,
    play_color: CardColor,
    draw_source: DrawSource,
    draw_color: CardColor | None = None,
) -> None:
    """
    Execute a full turn for the player.
    """
    put(play_card, player, play_target, play_color)
    draw(player, draw_source, draw_color)


# 3. When Game Finishes

# Scoring helpers and functions


def score_expedition(stack: Stack) -> int:
    """
    Compute score for a single expedition stack according to Lost Cities rules.
    Rules implemented:
      - Sum number cards (2..10); base = sum - 20 expedition cost.
      - Handshake (value 0) cards multiply total: multiplier = (handshakes + 1).
      - Empty expedition scores 0.
      - Expedition with only handshakes: base still -20 then multiplied.
    (Bonus for 8+ cards not implemented; add if needed.)
    """
    cards = stack.items
    if not cards:
        return 0
    handshake_count = sum(1 for c in cards if c.value == 0)
    number_sum = sum(c.value for c in cards if c.value != 0)
    base = number_sum - 20  # expedition investment cost
    return (handshake_count + 1) * base


def calculate_score(player: Player) -> int:
    """
    Total score across all expeditions for a player.
    """
    return sum(score_expedition(stack) for stack in player.expeditions.values())


def get_winner(p1: Player, p2: Player):
    """
    Return winning player or 'Draw'. Does not mutate players.
    """
    s1 = calculate_score(p1)
    s2 = calculate_score(p2)
    if s1 > s2:
        return p1
    if s2 > s1:
        return p2
    return "Draw"
