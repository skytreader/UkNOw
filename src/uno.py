from typing import Dict

import enum

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

    def __init__(self):
        self.deck: Dict[UnoCardType, int] = {}
        self.deck[UnoCardType.WILD] = 4
        self.deck[UnoCardType.WILDFOUR] = 4

        for color in CARD_COLORS:
            self.deck["%s_0" % color] = 1

            for n in range(1, 10):
                self.deck["%s_%d" % (color, n)] = 2

            for act in ACTION_CARDS:
                self.deck["%s_%s" % (color, act)] = 2

    def __len__(self):
        return sum([self.deck[k] for k in self.deck.keys()])
