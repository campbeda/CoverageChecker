#!/usr/bin/env python

'''Example test driver.'''

import unittest
# Import from top-level or from this directory
try:
    from lib import Foo
except ImportError:
    from example.lib import Foo

class TestFooCoverage(unittest.TestCase):
    def test_foo(self):
        print( 'TestFooCoverage: test_foo')
        foo = Foo(1,2)
        assert foo.getX() == 1
        assert foo.getY() == 2

if __name__ == "__main__":
    unittest.main() # pragma: no cover
