# test_reactor.py

from draftsman.entity import Reactor, reactors
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class ReactorTesting(TestCase):
    def test_constructor_init(self):
        reactor = Reactor()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Reactor(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Reactor("not a reactor")