# wierddict.py

class Foo:
    def __init__(self, d={}):
        self.data = d

class NewFoo:
    def __init__(self, d=None):
        if d==None:
            self.data = {}
        else:
            self.data = d

g = Foo()
print "g.data=%s" % g.data
g.data['bar'] = 'baz'
print "now g.data=%s" % g.data
h = Foo()
print "h.data=%s" % h.data

ng = NewFoo()
print "ng.data=%s" % ng.data
ng.data['bar'] = 'baz'
print "now ng.data=%s" % ng.data
nh = NewFoo()
print "nh.data=%s" % nh.data

def addn(n):
    return lambda x: x+n




#end