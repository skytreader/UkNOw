from collections import Counter
from .combinatorics import CombinationCount
from typing import Any, Dict, Iterable, List, Optional, Set

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
    WILDCARD_COUNT = 4
    DRAWFOUR_COUNT = 4
    ZERO_COUNT = 1
    NONZERO_COUNT = 2
    ACTION_CARD_COUNT = 2

    PER_COLOR_COUNT = 25
    PER_ZERO_COUNT = ZERO_COUNT * len(CardColor)
    PER_NONZERO_COUNT = NONZERO_COUNT * len(CardColor)
    PER_ACTION_CARD_COUNT = ACTION_CARD_COUNT * len(CardColor)

    def __init__(self):
        # This is a Dict rather than a Counter so we can easily remove card
        # instances that are exhausted in this deck instance.
        self.deck: Dict[UnoCard, int]= {}
        self.deck[UnoCard()] = UnoDeck.WILDCARD_COUNT
        self.deck[UnoCard(action=CardAction.DRAWFOUR)] = UnoDeck.DRAWFOUR_COUNT

        for color in list(CardColor):
            self.deck[UnoCard(color, 0)] = UnoDeck.ZERO_COUNT

            for n in range(1, 10):
                self.deck[UnoCard(color, n)] = UnoDeck.NONZERO_COUNT

            for act in list(CardAction):
                if act != CardAction.DRAWFOUR:
                    self.deck[UnoCard(color=color, action=act)] = UnoDeck.ACTION_CARD_COUNT

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

class CardCountsIndex(object):

    def __init__(self):
        self.total_counts: Counter[UnoCard] = Counter()
        self.color_counts: Counter[CardColor] = Counter()
        self.number_counts: Counter[int] = Counter()
        self.action_counts: Counter[CardAction] = Counter()

    def count(self, card: UnoCard):
        self.total_counts[card] += 1
        if card.color is not None:
            self.color_counts[card.color] += 1

        if card.number is not None:
            self.number_counts[card.number] += 1

        if card.action is not None:
            self.action_counts[card.action] += 1

class GameStateTracker(object):
    """
    Keeps track of the game state _from the perspective of one player_ and gives
    you odds for the best move.
    """

    def __init__(
            self,
            player_hand: List,
            other_players_card_counts: List[int],
        ):
        self.player_hand = player_hand
        self.other_players_card_counts = other_players_card_counts

        # We make use of an `UnoDeck` instance to keep track of cards we haven't
        # seen yet (i.e., not in hand nor in discarded, in other words, possibly
        # in play).
        self.unseen_cards = UnoDeck()
        self.seen_counter = CardCountsIndex()
        self.ORIGINAL_CARD_COUNT = len(self.unseen_cards)
        for card in self.player_hand:
            self.__see_card(card)

        # This is a parallel array to other_players_card_counts. This keeps
        # track of play requirements which the corresponding player was unable
        # to fulfill. This only keeps track of the _last_ such unfulfilled
        # requirement.
        self.unfulfilled_requirements_monitor: List[Optional[UnoCard]] = [
            None for _ in other_players_card_counts
        ]
        self.nCr = CombinationCount(self.ORIGINAL_CARD_COUNT).nCr

    def card_requirement_probability(self, card: UnoCard, next_player: int) -> float:
        """
        Given a card (in hand) what are the odds that the next player can
        fulfill the move requirement?
        """
        assert (
            (self.seen_counter.total_counts.total() + len(self.unseen_cards)) ==
            self.ORIGINAL_CARD_COUNT
        )
        # TODO Take wildcards into account
        # What are the odds next player has a card of the same color?
        player_hands_without_color_frac = 0.0
        if card.color is not None:
            remaining_color_unseen = (
                UnoDeck.PER_COLOR_COUNT - self.seen_counter.color_counts[card.color]
            )
            player_hand_universe = self.nCr(
                len(self.unseen_cards),
                self.other_players_card_counts[next_player]
            )
            player_hands_without_color = self.nCr(
                len(self.unseen_cards) - remaining_color_unseen,
                self.other_players_card_counts[next_player]
            )
            player_hands_without_color_frac = (
                player_hands_without_color / player_hand_universe
            )
        assert 0 <= player_hands_without_color_frac <= 1
        player_hand_has_color_prob = 1 - player_hands_without_color_frac

        # What are the odds next player has a card of the same number?
        player_hands_without_number_frac = 0.0
        if card.number is not None:
            remaining_number_unseen = (
                (UnoDeck.PER_NONZERO_COUNT if card.number else UnoDeck.PER_ZERO_COUNT)
                - self.seen_counter.number_counts[card.number]
            )
            player_hands_without_number = self.nCr(
                len(self.unseen_cards) - remaining_number_unseen,
                self.other_players_card_counts[next_player]
            )
            player_hands_without_number_frac = (
                player_hands_without_number / player_hand_universe
            )
        assert 0 <= player_hands_without_number_frac <= 1
        player_hand_has_number_prob = 1 - player_hands_without_number_frac

        # FIXME These hands have an intersection; does it matter?
        # FIXME This must be an OR because these two possibilities are
        # independent. However, can this return a value > 1?
        return (
            player_hand_has_color_prob + player_hand_has_number_prob
        )

    def count_deck(self) -> int:
        return (
            len(self.unseen_cards)
            - sum(self.other_players_card_counts)
        )

    # `ev_` methods translate directly to in-game events

    def __see_card(self, card: UnoCard):
        # The order is important here to keep the idempotent property of this
        # class. If seeing this card is "impossible", we want the unseen_cards
        # remove call to throw an exception so the rest of the method won't
        # happen anymore.
        self.unseen_cards.remove(card)
        self.seen_counter.count(card)

    def ev_initial_play(self, card: UnoCard):
        self.__see_card(card)

    def ev_other_player_played(
            self,
            player: int,
            card: Optional[UnoCard] = None
        ):
        if card is not None:
            self.__see_card(card)
            self.other_players_card_counts[player] -= 1
            assert self.other_players_card_counts[player] >= 0
        else:
            self.unfulfilled_requirements_monitor[player] = card

    def ev_other_player_drew(self, player: int, num_cards: int):
        if num_cards <= 0:
            raise ValueError("Players must draw at least one card.")
        self.other_players_card_counts[player] += num_cards

    def ev_player_drew(self, cards: Iterable[UnoCard]):
        for c in cards:
            self.__see_card(c)
            self.player_hand.append(c)

    def ev_player_played(self, card: UnoCard):
        self.__see_card(card)
