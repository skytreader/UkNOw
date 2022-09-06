from .uno import CardAction, CardColor, GameStateTracker, UnoCard, UnoDeck

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
        choice_mock.return_value = UnoCard(CardColor.RED, 0)
        self.assertEqual(choice_mock.return_value, self.deck.draw())
        self.assertEqual(0, self.deck.count(choice_mock.return_value))
        self.assertTrue(choice_mock.return_value not in self.deck.deck.keys())

    def test_draw_to_end(self):
        for _ in range(108):
            self.deck.draw()

        self.assertIsNone(self.deck.draw())
        self.assertEqual(0, len(self.deck))

    def test_remove_and_count(self):
        blue1 = UnoCard(CardColor.BLUE, 1)
        self.assertEqual(2, self.deck.count(blue1))
        self.deck.remove(blue1)
        self.assertEqual(1, self.deck.count(blue1))
        self.deck.remove(blue1)
        self.assertEqual(0, self.deck.count(blue1))
        self.assertRaises(Exception, self.deck.remove, blue1)

class UnoCardTest(unittest.TestCase):

    def test_matches_numeric_cards(self):
        green0 = UnoCard(CardColor.GREEN, 0)
        self.assertTrue(green0.matches(UnoCard(CardColor.GREEN, 1)))
        self.assertTrue(green0.matches(UnoCard(CardColor.RED, 0)))
        self.assertTrue(green0.matches(
            UnoCard(color=CardColor.GREEN, action=CardAction.SKIP))
        )
        # This is the wild card
        self.assertTrue(green0.matches(UnoCard()))
        # This is the wild four card
        self.assertTrue(green0.matches(UnoCard(action=CardAction.DRAWFOUR)))
        self.assertFalse(green0.matches(UnoCard(CardColor.RED, 1)))
        self.assertFalse(green0.matches(
            UnoCard(CardColor.RED, action=CardAction.SKIP))
        )

    def test_matches_wildcard(self):
        # When a player plays a wildcard, it "transforms" to a card with only a
        # color attribute which the next player must then match.
        green = UnoCard(CardColor.GREEN)
        self.assertTrue(green.matches(UnoCard(CardColor.GREEN, 1)))
        self.assertTrue(green.matches(
            UnoCard(color=CardColor.GREEN, action=CardAction.SKIP))
        )
        # This is the wild card
        self.assertTrue(green.matches(UnoCard()))
        # This is the wild four card
        self.assertTrue(green.matches(UnoCard(action=CardAction.DRAWFOUR)))
        self.assertFalse(green.matches(UnoCard(CardColor.RED, 1)))
        self.assertFalse(green.matches(
            UnoCard(CardColor.RED, action=CardAction.SKIP))
        )

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
