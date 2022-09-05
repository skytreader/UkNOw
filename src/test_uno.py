from .uno import CardPlayRequirement, GameStateTracker, UnoDeck, UnoCardType

from collections import Counter

import unittest
import unittest.mock

class UnoDeckTests(unittest.TestCase):

    def setUp(self):
        self.deck = UnoDeck()

    def test_deck_initial_state(self):
        self.assertEqual(len(self.deck), 108)

    @unittest.mock.patch("random.choice")
    def test_draw(self, choice_mock):
        choice_mock.return_value = UnoCardType.RED_0
        self.assertEqual(choice_mock.return_value, self.deck.draw())
        self.assertEqual(0, self.deck.count(choice_mock.return_value))
        self.assertTrue(choice_mock.return_value not in self.deck.deck.keys())

    def test_draw_to_end(self):
        for _ in range(108):
            self.deck.draw()

        self.assertIsNone(self.deck.draw())
        self.assertEqual(0, len(self.deck))

    def test_remove_and_count(self):
        self.assertEqual(2, self.deck.count(UnoCardType.BLUE_1))
        self.deck.remove(UnoCardType.BLUE_1)
        self.assertEqual(1, self.deck.count(UnoCardType.BLUE_1))
        self.deck.remove(UnoCardType.BLUE_1)
        self.assertEqual(0, self.deck.count(UnoCardType.BLUE_1))
        self.assertRaises(Exception, self.deck.remove, UnoCardType.BLUE_1)

class CardPlayRequirementTest(unittest.TestCase):

    def test_satisfies_numeric_cards(self):
        require_green_0 = CardPlayRequirement("GREEN", 0)
        self.assertTrue(require_green_0.is_satisfied(UnoCardType.GREEN_1.name))
        self.assertTrue(require_green_0.is_satisfied(UnoCardType.RED_0.name))
        self.assertTrue(require_green_0.is_satisfied(UnoCardType.GREEN_SKIP.name))
        self.assertTrue(require_green_0.is_satisfied(UnoCardType.WILD.name))
        self.assertTrue(require_green_0.is_satisfied(UnoCardType.WILDFOUR.name))
        self.assertFalse(require_green_0.is_satisfied(UnoCardType.RED_1.name))
        self.assertFalse(require_green_0.is_satisfied(UnoCardType.RED_SKIP.name))

    def test_wildcard(self):
        # The wildcard requirement is characterized as having no number specified
        require_wildcard = CardPlayRequirement("GREEN")
        self.assertTrue(require_wildcard.is_satisfied(UnoCardType.GREEN_1.name))
        self.assertTrue(require_wildcard.is_satisfied(UnoCardType.GREEN_0.name))
        self.assertTrue(require_wildcard.is_satisfied(UnoCardType.WILD.name))
        self.assertTrue(require_wildcard.is_satisfied(UnoCardType.WILDFOUR.name))
        self.assertFalse(require_wildcard.is_satisfied(UnoCardType.RED_0.name))
        self.assertFalse(require_wildcard.is_satisfied("GREEN"))

class GameStateTrackerTest(unittest.TestCase):
    """
    Testing strategy: we instantiate fields that basically mimic an ongoing
    game. Then the GameStateTracker instance is fed "scenarios" of the game
    happening. We can then check that this corresponds to the game we are
    simulating.
    """

    def setUp(self):
        # Create a game state that reflects the initial state of an Uno game.
        self.deck = UnoDeck()
        self.this_player = [self.deck.draw() for _ in range(7)]
        # Other players will draw cards; we don't care what those cards are
        for _ in range(3):
            for __ in range(7):
                self.deck.draw()

        self.current_discard = self.deck.draw()
        self.game_state_tracker = GameStateTracker(
            self.this_player,
            [7, 7, 7],
            Counter([self.current_discard])
        )

    def test_count(self):
        self.assertEqual(len(self.deck), self.game_state_tracker.count_deck())
