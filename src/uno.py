from typing import Dict, Set

import enum
import random

CARD_COLORS = ("RED", "YELLOW", "GREEN", "BLUE")
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
        self.non_zeros: Set[UnoCardType] = set([UnoCardType.WILD, UnoCardType.WILDFOUR])

        for color in CARD_COLORS:
            card_zero = UnoCardType["%s_0" % color]
            self.deck[card_zero] = 1
            self.non_zeros.add(card_zero)

            for n in range(1, 10):
                card_n = UnoCardType["%s_%d" % (color, n)]
                self.deck[card_n] = 2
                self.non_zeros.add(card_n)

            for act in ACTION_CARDS:
                action_card = UnoCardType["%s_%s" % (color, act)]
                self.deck[action_card] = 2
                self.non_zeros.add(action_card)

    def __len__(self):
        return sum([self.deck[k] for k in self.deck.keys()])

    def draw(self):
        """
        Randomly gets a card from the deck.
        """
        if self.non_zeros:
            card = random.choice(list(self.non_zeros))
            self.deck[card] -= 1
            if not self.deck[card]:
                self.non_zeros.remove(card)

            return card
        else:
            return None
