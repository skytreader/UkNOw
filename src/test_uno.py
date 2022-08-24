from .uno import CardPlayRequirement, UnoDeck, UnoCardType

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
        self.assertEqual(0, self.deck.deck[choice_mock.return_value])
        self.assertTrue(choice_mock.return_value not in self.deck.non_zeros)

    def test_draw_to_end(self):
        for _ in range(108):
            self.deck.draw()

        self.assertIsNone(self.deck.draw())
        self.assertEqual(0, len(self.deck))

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
