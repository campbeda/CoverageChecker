'''Example class library.'''

class Foo(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

class Bar(object):
    def __init__(self, name):
        self.name = name

    def getName(self):
        return self.name

class Baz(object):
    def __init__(self, num):
        self.num = 1
