# spilltypes.py = data tyes for Spill

""" Data types
Spill     Python
-----     ------
function  callable
string    LStr
symbol    str
int       int
list      list

Notation -- in Spill: (fred (x y) a "hello" 45)
implemented as Python: ['fred', ['x', 'y'], 'a', LStr("hello"), 45]
"""

#---------------------------------------------------------------------
"""SpillTypes have to implement:
show() -- equivlent of __repr__
showStr() -- equivalent of __str__
"""

class SpillType:
    """ abstract superclass for all spill types that are not
    predefined python types.
    """
    pass

class LStr(SpillType):
    def __init__(self, s):
        self.s = s
    def __eq__(self, anLStr):
        if not isinstance(anLStr, LStr):
            raise NotImplemented
        return self.s==anLStr.s
    def __ne__(self, anLStr):
        return not self.__eq__(anLStr)

    def __str__(self): return self.s
    showStr = __str__

    def __repr__(self):
        return "LStr(%r)" % (self.s,)

    def show(self):
        retval = '"'
        for ch in self.s:
            if ch=="\n": retval += r"\n"
            elif ch=="\\": retval += r"\\"
            elif ch=='"': retval += r'\"'
            else:
                retval += ch
        #//for
        retval += '"'
        return retval

#---------------------------------------------------------------------

def show(ex):
    """ display an s-expression in a form that will re-create the object
    if possible (similar to python __repr__)
    @return [str]
    """
    if isinstance(ex, SpillType):
        return ex.show()
    if type(ex)==tuple:
        contents = " ".join([show(item) for item in ex])
        return "(" + contents + ")"
    return str(ex)


def showStr(ex):
    """ display an s-expression in a form suitable for printing
    (similar to python __str__)
    @return [str]
    """
    if isinstance(ex, SpillType):
        return ex.showStr()
    return show(ex)


#---------------------------------------------------------------------
# utility functions

def exToList(ex):
    """ convert an s-expression to a Python list
    """
    if isinstance(ex, tuple):
        return [exToList(e) for e in ex]
    else:
       return ex


#---------------------------------------------------------------------

#end
