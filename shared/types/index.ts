
/* Card Configurations */

/**
 * Represents the six expedition colors available in Lost Cities.
 * Each color corresponds to a different expedition route that players can explore.
 * 
 * @example
 * ```typescript
 * const expeditionColor: CardColor = 'RED';
 * ```
 */
export type CardColor = 'RED' | 'BLUE' | 'GREEN' | 'YELLOW' | 'WHITE' | 'PURPLE';

/**
 * Represents the possible values for cards in Lost Cities.
 * - Value 0: Handshake cards (investment/wager cards that multiply expedition scores)
 * - Values 2-10: Number cards that advance expeditions and contribute to scoring
 * 
 * Note: There is no value 1 in Lost Cities - the sequence goes 0 (handshake), 2, 3, 4, 5, 6, 7, 8, 9, 10
 * 
 * @example
 * ```typescript
 * const handshakeCard: CardValue = 0;  // Investment card
 * const numberCard: CardValue = 5;     // Expedition card worth 5 points
 * ```
 */
export type CardValue = 0 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;

/**
 * Represents a single card in the Lost Cities game.
 * Each card belongs to one of six expedition colors and has a specific value.
 * 
 * @interface Card
 * @property {CardColor} color - The expedition color this card belongs to
 * @property {CardValue} value - The numeric value of the card (0 for handshake, 2-10 for number cards)
 * 
 * @example
 * ```typescript
 * const redHandshake: Card = { color: 'RED', value: 0 };
 * const blueExpedition: Card = { color: 'BLUE', value: 7 };
 * ```
 */
export interface Card {
    color: CardColor;
    value: CardValue;
}

export interface Stack<T> {
    items: T[];
}


/* Player Configurations */

/**
 * Represents a player in the Lost Cities game.
 * Each player maintains their own hand of cards and expedition boards.
 * 
 * @interface Player
 * @property {Card[]} hand - The cards currently in the player's hand (typically 8 cards)
 * @property {Record<CardColor, Card[]>} expeditions - The player's expedition boards, 
 *   organized by color. Each expedition contains cards played in ascending order.
 *   Handshake cards (value 0) must be played before number cards and multiply the final score.
 * 
 * @example
 * ```typescript
 * const player: Player = {
 *   hand: [
 *     { color: 'RED', value: 5 },
 *     { color: 'BLUE', value: 0 }
 *   ],
 *   expeditions: {
 *     'RED': [{ color: 'RED', value: 2 }, { color: 'RED', value: 4 }],
 *     'BLUE': [],
 *     'GREEN': [{ color: 'GREEN', value: 0 }], // Handshake card played
 *     'YELLOW': [],
 *     'WHITE': [],
 *     'PURPLE': []
 *   }
 * };
 * ```
 */
export interface Player {
    hand: Card[];
    expeditions: Record<CardColor, Card[]>;
}

/* Game Configurations */

/**
 * Represents the current phase of a Lost Cities game turn.
 * Each turn consists of two phases that must be completed in order.
 * 
 * - PLAY: Player must play or discard one card from their hand
 * - DRAW: Player must draw one card from either the deck or a discard pile
 * - GAME_OVER: The game has ended (typically when the deck is exhausted)
 * 
 * @example
 * ```typescript
 * let currentPhase: GamePhase = 'PLAY';  // Player needs to play a card
 * // After playing a card...
 * currentPhase = 'DRAW';  // Player needs to draw a card
 * ```
 */
export type GamePhase = 'PLAY' | 'DRAW' | 'GAME_OVER';

/**
 * Represents the complete state of a Lost Cities game.
 * Contains all information needed to render the game and determine valid moves.
 * 
 * @interface GameState
 * @property {[Player, Player]} players - Exactly two players in the game (tuple for type safety)
 * @property {0 | 1} currentPlayer - Index of the player whose turn it is (0 or 1)
 * @property {GamePhase} phase - Current phase of the active player's turn
 * @property {Card[]} deck - Remaining cards in the draw deck (face down)
 * @property {Record<CardColor, Stack<Card>>} discardPiles - Six discard piles (one per color),
 *   where only the top card of each stack is visible and can be drawn by players.
 *   Each pile follows LIFO (Last In, First Out) behavior.
 * 
 * @example
 * ```typescript
 * const gameState: GameState = {
 *   players: [player1, player2],
 *   currentPlayer: 0,     // Player 1's turn
 *   phase: 'PLAY',        // Waiting for player to play a card
 *   deck: [...],          // Remaining cards to draw
 *   discardPiles: {
 *     'RED': { items: [{ color: 'RED', value: 3 }] },   // Stack with RED 3 on top
 *     'BLUE': { items: [] },                            // Empty discard pile
 *     'GREEN': { items: [...] },
 *     'YELLOW': { items: [...] },
 *     'WHITE': { items: [...] },
 *     'PURPLE': { items: [...] }
 *   }
 * };
 * ```
 */
export interface GameState {
    players: [Player, Player];
    currentPlayer: 0 | 1;
    phase: GamePhase;
    deck: Card[];
    discardPiles: Record<CardColor, Stack<Card>>;
}
