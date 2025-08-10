"""Tests for `domains.game.service` covering init, actions, and scoring."""

import pytest

from domains.game import service
from shared_types import COLORS, Card, Player, Stack


def test_init_game_reproducible():
    """init_game with a fixed seed yields identical deck and hands for both players."""
    g1 = service.init_game(seed=123)
    g2 = service.init_game(seed=123)
    # Deck order and hands should match for fixed seed
    assert g1.deck == g2.deck
    assert g1.players[0].hand == g2.players[0].hand
    assert g1.players[1].hand == g2.players[1].hand
    # 8 cards each
    assert len(g1.players[0].hand) == 8
    assert len(g1.players[1].hand) == 8
    # Total cards accounted for
    full_deck_size = len(COLORS) * (3 + 9)  # 3 handshake + 2..10
    assert len(g1.deck) + 16 == full_deck_size


def test_put_discard(game_state):
    """Playing to discard removes one card from hand and pushes it onto the correct pile."""
    p = game_state.players[0]
    card = p.hand[0]
    initial_hand_size = len(p.hand)
    service.put(game_state, card, p, target="discard", color=card.color)
    assert len(p.hand) == initial_hand_size - 1
    assert game_state.discard_piles[card.color].items[-1] == card


def test_put_expedition_valid_sequence(game_state):
    """Allows non-decreasing number sequence on an expedition (e.g., 2 then 5)."""
    p = game_state.players[0]
    # Construct ascending expedition manually
    ccolor = COLORS[0]
    c2 = Card(color=ccolor, value=2)
    c5 = Card(color=ccolor, value=5)
    p.hand.extend([c2, c5])
    service.put(game_state, c2, p, target="expedition", color=ccolor)
    service.put(game_state, c5, p, target="expedition", color=ccolor)
    assert [c.value for c in p.expeditions[ccolor].items] == [2, 5]


def test_put_expedition_invalid_descending(game_state):
    """Disallows placing a lower number after a higher one; raises ValueError."""
    p = game_state.players[0]
    ccolor = COLORS[1]
    c5 = Card(color=ccolor, value=5)
    c2 = Card(color=ccolor, value=2)
    p.hand.extend([c5, c2])
    service.put(game_state, c5, p, target="expedition", color=ccolor)
    with pytest.raises(ValueError):
        service.put(game_state, c2, p, target="expedition", color=ccolor)


def test_put_card_not_in_hand(game_state):
    """Rejects attempting to play a card the player does not hold."""
    p = game_state.players[0]
    other = Card(color=COLORS[0], value=2)
    with pytest.raises(ValueError):
        service.put(game_state, other, p, target="discard", color=COLORS[0])


def test_draw_from_deck(game_state):
    """Drawing from the deck appends the card to hand and reduces deck size by one."""
    p = game_state.players[0]
    deck_len_before = len(game_state.deck)
    new_card = service.draw(game_state, p, source="deck")
    assert new_card in p.hand
    assert len(game_state.deck) == deck_len_before - 1


def test_draw_from_empty_deck():
    """Cannot draw from an empty deck; raises ValueError."""
    g = service.init_game(seed=1)
    # Exhaust deck
    g.deck.clear()
    p = g.players[0]
    with pytest.raises(ValueError):
        service.draw(g, p, source="deck")


def test_draw_from_discard(game_state):
    """Drawing from a discard pile returns and adds the top card of that color to the hand."""
    p = game_state.players[0]
    # First place a known card into discard
    card = p.hand[0]
    service.put(game_state, card, p, target="discard", color=card.color)
    drawn = service.draw(game_state, p, source="discard", color=card.color)
    assert drawn == card
    assert drawn in p.hand


def test_draw_from_empty_discard(game_state):
    """Cannot draw from an empty color discard pile; raises ValueError."""
    p = game_state.players[0]
    empty_color = COLORS[2]
    with pytest.raises(ValueError):
        service.draw(game_state, p, source="discard", color=empty_color)


def test_turn_executes_put_then_draw(game_state):
    """A turn performs put then draw: discard updated and hand size stays constant."""
    p = game_state.players[0]
    starting_hand = p.hand.copy()
    play_card = starting_hand[0]
    service.turn(
        game_state,
        p,
        play_card=play_card,
        play_target="discard",
        play_color=play_card.color,
        draw_source="deck",
    )
    # Verify the discard pile has the played card
    assert game_state.discard_piles[play_card.color].items[-1] == play_card
    assert len(p.hand) == len(starting_hand)  # discarded 1 drew 1


def test_score_expedition_empty():
    """An empty expedition scores 0 points."""
    st = Stack()
    assert service.score_expedition(st) == 0


def test_score_expedition_with_handshakes_and_numbers():
    """Scoring combines (sum-20) base with handshake multiplier (handshakes+1)."""
    st = Stack()
    st.items.extend(
        [
            Card(color=COLORS[0], value=0),
            Card(color=COLORS[0], value=0),
            Card(color=COLORS[0], value=2),
            Card(color=COLORS[0], value=5),
        ]
    )
    # number sum = 7; base = 7 - 20 = -13; handshakes=2 => multiplier 3 => -39
    assert service.score_expedition(st) == -39


def test_calculate_score_and_get_winner():
    """Sums all expedition scores and returns the player with the higher total."""
    p1 = Player()
    p2 = Player()
    color = COLORS[0]
    # p1 expedition: handshake + 2 + 4 => number sum=6 base=-14 multiplier=2 => -28
    p1.expeditions[color].items.extend(
        [
            Card(color=color, value=0),
            Card(color=color, value=2),
            Card(color=color, value=4),
        ]
    )
    # p2 expedition: 2 + 3 + 10 => sum=15 base=-5 multiplier=1 => -5 (better)
    p2.expeditions[color].items.extend(
        [
            Card(color=color, value=2),
            Card(color=color, value=3),
            Card(color=color, value=10),
        ]
    )
    s1 = service.calculate_score(p1)
    s2 = service.calculate_score(p2)
    assert s1 == -28
    assert s2 == -5
    assert service.get_winner(p1, p2) == p2


def test_get_winner_draw():
    """Returns 'Draw' when both players have the same total score."""
    p1 = Player()
    p2 = Player()
    assert service.get_winner(p1, p2) == "Draw"
