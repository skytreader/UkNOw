from typing import Dict, Literal, Optional, Set

import enum
import random

CARD_COLORS = ("RED", "YELLOW", "GREEN", "BLUE")
CARD_COLORS_TYPE = Literal["RED", "YELLOW", "GREEN", "BLUE"]
ACTION_CARDS = ("SKIP", "DRAWTWO", "REVERSE")

def create_cardtype_enum():
    deck = {
        "WILD": enum.auto(),
        "WILDFOUR": enum.auto(),
    }

    for c in CARD_COLORS:
        for i in range(10):
            deck["_".join((c, str(i)))] = enum.auto()

        for label in ACTION_CARDS:
            deck["_".join((c, label))] = enum.auto()

    return enum.Enum("UnoCard", deck)

UnoCardType = create_cardtype_enum()

class UnoDeck(object):
    """
    Stateful representation of an Uno Deck. Each method is constant time
    (i.e., Big-O is bounded by the 108 card count, never an integral multiple).
    """

    def __init__(self):
        self.deck: Dict[UnoCardType, int] = {}
        self.deck[UnoCardType.WILD] = 4
        self.deck[UnoCardType.WILDFOUR] = 4

        for color in CARD_COLORS:
            card_zero = UnoCardType["%s_0" % color]
            self.deck[card_zero] = 1

            for n in range(1, 10):
                card_n = UnoCardType["%s_%d" % (color, n)]
                self.deck[card_n] = 2

            for act in ACTION_CARDS:
                action_card = UnoCardType["%s_%s" % (color, act)]
                self.deck[action_card] = 2

    def __len__(self):
        return sum([self.deck[k] for k in self.deck.keys()])

    def draw(self):
        """
        Randomly gets a card from the deck. This effective removes the card from
        the deck.
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

    def count(self, card) -> Optional[int]:
        if card in UnoCardType:
            return self.deck.get(card, 0)
        else:
            return None

class CardPlayRequirement(object):

    def __init__(self, color: CARD_COLORS_TYPE, number: Optional[int] = None):
        self.color = color
        self.number = number

    def is_satisfied(self, card: str) -> bool:
        """
        You can get valid arguments via the `name` field of the `UnoCardType`
        enum.
        """
        if card in (UnoCardType.WILD.name, UnoCardType.WILDFOUR.name):
            return True

        cardparse = card.split("_")
        if self.number is not None:
            try:
                return self.color == cardparse[0] or self.number == int(cardparse[1])
            except ValueError:
                return False
        else:
            return len(cardparse) == 2 and self.color == cardparse[0]

class PlayerActionConstraints(object):

    def __init__(self, must_draw: int, must_play: CardPlayRequirement):
        self.must_draw = must_draw
        self.must_play = must_play
