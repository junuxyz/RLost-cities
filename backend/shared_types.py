from dataclasses import dataclass, field
from typing import Literal

# Card Configurations

"""
Represents the six expedition colors available in Lost Cities.
Each color corresponds to a different expedition route that players can explore.
Example:
    expedition_color: CardColor = 'RED'
"""
# Define Literal explicitly (works on older Python versions). Then single runtime source COLORS typed with CardColor.
CardColor = Literal["RED", "BLUE", "GREEN", "YELLOW", "WHITE", "PURPLE"]
COLORS: tuple[CardColor, ...] = ("RED", "BLUE", "GREEN", "YELLOW", "WHITE", "PURPLE")

# Draw / play target aliases (shared by logic & other modules)
DrawSource = Literal["deck", "discard"]
PlayTarget = Literal["expedition", "discard"]


"""
Represents the possible values for cards.
- Value 0: Handshake cards (investment/wager cards that multiply expedition scores)
- Values 2-10: Number cards that advance expeditions and contribute to scoring
Note: There is no value 1 in Lost Cities - the sequence goes 0 (handshake), 2, 3, ..., 10
Example:
    handshake_card: CardValue = 0  # Investment card
    number_card: CardValue = 5     # Expedition card worth 5 points
"""
CardValue = Literal[0, 2, 3, 4, 5, 6, 7, 8, 9, 10]


@dataclass(frozen=True)
class Card:
    """
    Represents a single card in the Lost Cities game.
    Each card belongs to one of six expedition colors and has a specific value.
    Attributes:
        color: The expedition color this card belongs to
        value: The numeric value of the card (0 for handshake, 2-10 for number cards)
    Example:
        red_handshake = Card(color='RED', value=0)
        blue_expedition = Card(color='BLUE', value=7)
    """

    color: CardColor
    value: CardValue


@dataclass
class Stack:
    """
    Represents a stack of cards (LIFO).
    """

    items: list[Card] = field(default_factory=list)


# Player Configurations


@dataclass
class Player:
    """
    Represents a player in the Lost Cities game.
    Each player maintains their own hand of cards and expedition boards.
    Attributes:
        hand: The cards currently in the player's hand (typically 8 cards)
        expeditions: The player's expedition boards, organized by color. Each expedition contains cards played in ascending order. Handshake cards (value 0) must be played before number cards and multiply the final score.
        score: The player's final score. This is set to 0 as default and calculated at the end of the game.
    Example:
        player = Player(
            hand=[Card(color='RED', value=5), Card(color='BLUE', value=0)],
            expeditions={
                'RED': [Card(color='RED', value=2), Card(color='RED', value=4)],
                'BLUE': [],
                'GREEN': [Card(color='GREEN', value=0)],
                'YELLOW': [],
                'WHITE': [],
                'PURPLE': []
            }
            score = 0
        )
    """

    hand: list[Card] = field(default_factory=list)
    expeditions: dict[CardColor, Stack] = field(
        default_factory=lambda: {c: Stack() for c in COLORS}
    )
    score: int = 0


# Game Configurations

GamePhase = Literal["PLAY", "DRAW", "GAME_OVER"]
"""
Represents the current phase of a Lost Cities game turn.
Each turn consists of two phases that must be completed in order.
- PLAY: Player must play or discard one card from their hand
- DRAW: Player must draw one card from either the deck or a discard pile
- GAME_OVER: The game has ended (typically when the deck is exhausted)
Example:
    current_phase: GamePhase = 'PLAY'
    # After playing a card...
    current_phase = 'DRAW'
"""


@dataclass
class GameState:
    """
    Represents the complete state of a Lost Cities game.
    Contains all information needed to render the game and determine valid moves.
    Attributes:
        players: Exactly two players in the game (tuple for type safety)
        current_player: Index of the player whose turn it is (0 or 1)
        phase: Current phase of the active player's turn
        deck: Remaining cards in the draw deck (face down)
        discard_piles: List that contains discard piles and each player's expeditions.
            - expeditions: each player's expedition.
            - discard_piles: Six discard piles (one per color), where only the top card of each stack is visible and can be drawn by players. Each pile follows LIFO (Last In, First Out) behavior.
    Example:
        p1 = Player(
            hand=[Card(color='RED', value=5)],
            expeditions={
                'RED': [Card(color='RED', value=0), Card(color='RED', value=2)],
                'BLUE': [], 'GREEN': [], 'YELLOW': [], 'WHITE': [], 'PURPLE': []
            }
        )
        p2 = Player(
            hand=[Card(color='BLUE', value=3)],
            expeditions={
                'RED': [], 'BLUE': [Card(color='BLUE', value=2)], 'GREEN': [], 'YELLOW': [], 'WHITE': [], 'PURPLE': []
            }
        )
        game_state = GameState(
            players=(p1, p2),
            current_player=0,
            phase='PLAY',
            deck=[Card(color='GREEN', value=4), Card(color='YELLOW', value=6)],
            discard_piles={
                'RED': Stack(items=[Card(color='RED', value=3)]),
                'BLUE': Stack(items=[]),
                'GREEN': Stack(items=[]),
                'YELLOW': Stack(items=[]),
                'WHITE': Stack(items=[]),
                'PURPLE': Stack(items=[])
            }
        )
    """

    players: tuple[Player, Player]
    current_player: int  # 0 or 1
    phase: GamePhase
    deck: list[Card] = field(default_factory=list)
    discard_piles: dict[CardColor, Stack] = field(
        default_factory=lambda: {c: Stack() for c in COLORS}
    )
