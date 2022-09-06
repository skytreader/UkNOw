from collections import Counter
from typing import Any, Dict, List, Optional, Set

import enum
import random

@enum.unique
class CardColor(enum.Enum):
    RED = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()
    BLUE = enum.auto()

@enum.unique
class CardAction(enum.Enum):
    SKIP = enum.auto()
    DRAWTWO = enum.auto()
    DRAWFOUR = enum.auto()
    REVERSE = enum.auto()

def _attr_cmp(a, b):
    return a is not None and a is b

class UnoCard(object):

    def __init__(
            self,
            color: Optional[CardColor] = None, 
            number: Optional[int] = None,
            action: Optional[CardAction] = None
        ):
        self.color = color
        self.number = number
        self.action = action

    @staticmethod
    def is_wildcard(card: "UnoCard"):
        return card.color is None and card.number is None

    def matches(self, card: "UnoCard"):
        return (
            UnoCard.is_wildcard(self) or
            UnoCard.is_wildcard(card) or
            _attr_cmp(self.color, card.color) or
            _attr_cmp(self.number, card.number) or
            _attr_cmp(self.action, card.action)
        )

    def __hash__(self):
        return hash((self.color, self.number, self.action))
    
    def __eq__(self, other):
        return (
            self.color is other.color and
            self.number is other.number and
            self.action is other.action
        )

class UnoDeck(object):
    """
    Stateful representation of an Uno Deck. Each method is constant time
    (i.e., Big-O is bounded by the 108 card count, never an integral multiple).
    """

    def __init__(self):
        # This is a Dict rather than a counter so we can easily remove card
        # instances that are exhausted in this deck instance.
        self.deck: Dict[UnoCard, int]= {}
        self.deck[UnoCard()] = 4
        self.deck[UnoCard(action=CardAction.DRAWFOUR)] = 4

        for color in list(CardColor):
            self.deck[UnoCard(color, 0)] = 1

            for n in range(1, 10):
                self.deck[UnoCard(color, n)] = 2

            for act in list(CardAction):
                if act != CardAction.DRAWFOUR:
                    self.deck[UnoCard(color=color, action=act)] = 2

    def __len__(self):
        return sum([self.deck[k] for k in self.deck.keys()])

    def draw(self):
        """
        Randomly gets a card from the deck. This effectively removes the card
        from the deck.
        """
        ks = list(self.deck.keys())
        if ks:
            card = random.choice(ks)
            self.deck[card] -= 1
            assert self.deck[card] >= 0
            if not self.deck[card]:
                del self.deck[card]

            return card
        else:
            return None

    def remove(self, card: UnoCard):
        """
        Remove that specific card from the deck.
        """
        self.deck[card] -= 1
        if not self.deck[card]:
            del self.deck[card]

    def count(self, card: UnoCard) -> Optional[int]:
        return self.deck.get(card, 0)

class GameStateTracker(object):
    """
    Keeps track of the game state _from the perspective of one player_ and gives
    you odds for the best move.
    """

    def __init__(
            self,
            player_hand: List,
            other_players_card_counts: List[int],
            discard_pile: Counter
        ):
        self.player_hand = player_hand
        self.other_players_card_counts = other_players_card_counts

        # We make use of an `UnoDeck` instance to keep track of cards we haven't
        # seen yet (i.e., not in hand nor in discarded).
        self.unseen_cards = UnoDeck()
        for card in self.player_hand:
            self.unseen_cards.remove(card)

        # This is a parallel array to other_players_card_counts. This keeps
        # track of play requirements which the corresponding player was unable
        # to fulfill. This only keeps track of the _last_ such unfulfilled
        # requirement.
        self.unfulfilled_requirements_monitor: List[Optional[UnoCard]] = [
            None for _ in other_players_card_counts
        ]
        self.discard_pile: Counter = discard_pile

    def card_requirement_probability(self, card, next_player):
        """
        Given a card (in hand) what are the odds that the next player can
        fulfill the move requirement?
        """
        pass

    def count_deck(self) -> int:
        return (
            len(self.unseen_cards)
            - sum(self.other_players_card_counts)
            - self.discard_pile.total()
        )

    # `ev_` methods translate directly to in-game events

    def ev_other_player_played(
            self,
            player: int,
            card: Optional[UnoCard] = None
        ):
        if card is not None:
            self.unseen_cards.remove(card)
            self.discard_pile[card] += 1
            self.other_players_card_counts[player] -= 1
            assert self.other_players_card_counts[player] >= 0
        else:
            self.unfulfilled_requirements_monitor[player] = card

    def ev_other_player_drew(self, player: int, num_cards: int):
        if num_cards <= 0:
            raise ValueError("Players must draw at least one card.")
        self.other_players_card_counts[player] += num_cards
