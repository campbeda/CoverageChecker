'''Example test driver.'''

from lib import Foo

foo = Foo(1,2)
assert foo.getX() == 1
assert foo.getY() == 2
