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
        deck: Dict[UnoCardType, int] = {}
        deck[UnoCardType.WILD] = 4
        deck[UnoCardType.WILDFOUR] = 4
