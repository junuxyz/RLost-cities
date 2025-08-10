import random
from typing import cast

from typing_extensions import assert_never

from shared_types import (
    COLORS,
    Card,
    CardColor,
    CardValue,
    DrawSource,
    GameState,
    Player,
    PlayTarget,
    Stack,
)

# Game initialization -------------------------------------------------------


def init_game(seed=None) -> GameState:
    """Create and return a freshly initialized GameState.

    Args:
        seed: Optional RNG seed for reproducible shuffles (used for tests).

    Deck construction rules:
        Per color -> 3 handshake (0) + numbers 2-10 (inclusive)
    Dealing:
        8 cards to each player (after shuffling). Top-of-deck is the *end* of
        the list stored in GameState.deck (so draws use pop()).
    """
    if seed is not None:
        random.seed(seed)

    # Build full raw deck
    raw_deck: list[Card] = []
    for c in COLORS:
        for _ in range(3):
            raw_deck.append(Card(color=c, value=0))
        for v in range(2, 11):
            raw_deck.append(Card(color=c, value=cast(CardValue, v)))

    random.shuffle(raw_deck)

    # We'll treat the *end* of the list as the top of the deck for O(1) pops.
    # (Earlier version used deque + popleft). Keeping list simplifies dataclass.

    p1 = Player()
    p2 = Player()

    # Deal 8 each (total removed: 16 cards)
    for _ in range(8):
        p1.hand.append(raw_deck.pop())
        p2.hand.append(raw_deck.pop())

    discard_piles = {c: Stack() for c in COLORS}

    return GameState(
        players=(p1, p2),
        current_player=0,
        phase="PLAY",
        deck=raw_deck,  # remaining cards (top = end)
        discard_piles=discard_piles,
    )


# Game actions --------------------------------------------------------------


def put(
    game: GameState,
    card: Card,
    player: Player,
    target: PlayTarget,
    color: CardColor,
) -> None:
    """Place a card from player's hand either onto an expedition or a discard pile.
    'color' indicates which expedition or discard pile.
    """
    if card not in player.hand:
        raise ValueError("Player does not have that card")

    if target == "discard":
        game.discard_piles[color].items.append(card)
        player.hand.remove(card)
        return
    elif target == "expedition":
        stack = player.expeditions[color].items
        last_numbers = [c.value for c in stack if c.value != 0]
        if last_numbers and card.value < last_numbers[-1]:
            raise ValueError("Number card must be >= previous number card")
        stack.append(card)
        player.hand.remove(card)
        return
    else:
        assert_never(target)


def draw(
    game: GameState,
    player: Player,
    source: DrawSource,
    color: "CardColor | None" = None,
) -> Card:
    """Draw a card for player from deck or a specific discard pile.
    If drawing from discard, a color must be provided. Returns drawn card.
    """
    if source == "deck":
        if not game.deck:
            raise ValueError("Deck is empty")
        card = game.deck.pop()  # top = end
        player.hand.append(card)
        return card
    elif source == "discard":
        if color is None:
            raise ValueError("Color required when drawing from discard")
        pile = game.discard_piles[color].items
        if not pile:
            raise ValueError(f"Discard pile {color} is empty")
        card = pile.pop()  # LIFO
        player.hand.append(card)
        return card


def turn(
    game: GameState,
    player: Player,
    play_card: Card,
    play_target: PlayTarget,
    play_color: CardColor,
    draw_source: DrawSource,
    draw_color: "CardColor | None" = None,
) -> None:
    """Execute a full turn for the player (play/discard then draw)."""
    put(game, play_card, player, play_target, play_color)
    draw(game, player, draw_source, draw_color)


# Scoring ------------------------------------------------------------------


def score_expedition(stack: Stack) -> int:
    """Compute score for a single expedition stack.

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
    base = number_sum - 20
    return (handshake_count + 1) * base


def calculate_score(player: Player) -> int:
    """Total score across all expeditions for a player."""
    return sum(score_expedition(stack) for stack in player.expeditions.values())


def get_winner(p1: Player, p2: Player):
    """Return winning player or 'Draw'."""
    s1 = calculate_score(p1)
    s2 = calculate_score(p2)
    if s1 > s2:
        return p1
    if s2 > s1:
        return p2
    return "Draw"
