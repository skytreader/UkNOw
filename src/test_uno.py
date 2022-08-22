from .uno import UnoDeck

def test_deck_initial_state():
    assert len(UnoDeck()) == 108
