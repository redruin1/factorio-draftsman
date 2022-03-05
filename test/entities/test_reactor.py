# test_reactor.py

from draftsman.entity import Reactor, reactors
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class ReactorTesting(TestCase):
    def test_default_constructor(self):
        reactor = Reactor()
        self.assertEqual(
            reactor.to_dict(),
            {
                "name": "nuclear-reactor",
                "position": {"x": 2.5, "y": 2.5}
            }
        )

    def test_constructor_init(self):
        reactor = Reactor()

        # Warnings
        with self.assertWarns(UserWarning):
            Reactor(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            Reactor("not a reactor")