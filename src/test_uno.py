from .uno import UnoDeck, UnoCardType

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
