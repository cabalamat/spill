# spill.py = short practical implementation of a Lisplike language

import sys

import addpath
import butil

from decspill import *
import spilltypes
import lexer
import parser

debug = 0
isa = isinstance

#---------------------------------------------------------------------
""" Environments

An environment is a list of variables and bindings. The top-level
binding contains global variables and primitive (built-in) functions
"""

class VariableNotFound(Exception): pass

class Environment:
    def __init__(self, parent=None, initialValue=None):
        self.parent = parent
        if initialValue == None:
            self.data = {}
        else:
            self.data = initialValue

    def get(self, k):
        """ return the value of (k)
        @param k [str]
        """
        if self.data.has_key(k):
            return self.data[k]
        elif self.parent!=None:
            return self.parent.get(k)
        else:
            raise VariableNotFound("Can't find variable '%s'" % (k,))
    __getitem__ = get

    def define(self, k, value):
        """ create a new variable in this environment """
        self.data[k] = value

    def getEnvFor(self, var):
        """ return the innermost environment that includes (var) """
        if self.data.has_key(var): return self
        if self.parent!=None: self.parent.getEnvFor(var)
        raise VariableNotFound("Can't find variable '%s'" % (var,))

    def debugPrintVars(self, level=0):
        """ print our variables for debugging """
        print "***** environment %d *****" % level
        keys = self.data.keys()
        keys.sort()
        for k in keys:
            print "%s = %r" % (k, self.data[k])
        if self.parent: parent.deubugPrintVars(level+1)

#---------------------------------------------------------------------
""" primitives
"""

class Primitive:
    def __init__(self, f, desc=None):
        self.f = f
        self.desc = desc
        if not self.desc:
            try:
                self.desc = f.__name__
            except:
                self.desc = repr(f)

    def __repr__(self):
        return "<prim:%s>" % self.desc

    def __call__(self, *args):
        if debug:
            print "calling %s args=%r" % (self, args)
        return self.f(*args)

def spillTrue(v):
    """ does a value count as a true value in spill?
    false values are 'false', 0, [], LStr("").
    Everything else is true.
    @return 'true'|'false'
    """
    if v=='false' or v==0 or v==[]: return 'false'
    if isa(v, spilltypes.LStr) and v.s=="":
        return 'false'
    return 'true'

def spillEq(x, y):
    return spillTrue(x==y)

def isPair(x):
    """ is (x) a list of length at least 1? """
    return isa(x, tuple) and len(x)>0

def append(*lists):
    """ catenate lists """
    result = []
    for a in lists:
        result = result + list(a)
    return tuple(result)


def pr(*args):
    """ print the arguments to stdout """
    #print "pr(args=%r)" % (args,)
    outStr = "".join([spilltypes.showStr(arg) for arg in args])
    sys.stdout.write(outStr)
    return spilltypes.LStr(outStr)

import operator
primitives = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.div,
    'car': lambda a: a[0],
    'cdr': lambda a: a[1:],
    'cons': lambda x, xs: tuple([x]+list(xs)),
    'null?': lambda a: a==(),
    'pair?': isPair,
    'append': append,
    '?': spillTrue,
    'eq?': lambda x,y: x==y,
    '==': lambda x,y: x==y,
    '>': lambda x,y: spillTrue(x>y),
    '<': lambda x,y: spillTrue(x<y),
    '>=': lambda x,y: spillTrue(x<y),
    '<=': lambda x,y: spillTrue(x<y),
    'eq?': spillEq,
    '==': spillEq,
    '!=': lambda x,y: spillTrue(not(x==y)),
    'pr': pr
}

def addPrimitivesToEnv(env):
    for k,v in primitives.items():
        p = Primitive(v, k)
        env.data[k] = p

#---------------------------------------------------------------------
""" closures
"""

class Closure:
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env

    def __repr__(self):
        return "<closure %s %s>" %\
           (spilltypes.show(self.params),
            spilltypes.show(self.body))

    def __call__(self, *args):
        if debug: print "calling %s\n        args=%r" % (self, args)
        paramBindings = {}
        for ix in range(len(args)):
            if self.params[ix]=='*':
                paramBindings[self.params[ix+1]] = tuple(args[ix:])
                #print "bindings=%r" % (paramBindings,)
                break
            else:
                paramBindings[self.params[ix]] = args[ix]
        newEnv = Environment(self.env, paramBindings)
        return seval(self.body, newEnv)


#---------------------------------------------------------------------
""" spill evaluation

This evaluates an s-expression (x) in an environment (env).

Special forms are:
   (fn ...) = forms a closure
   (quote x) = returns x, not evaluating it
   (if c1 ex1
       c2 ex2
       c3 ex3) = evaluates conditions c[n] until one is true,
                 then evaluates the corresponding ex[n].
"""

#@evalargs
def seval(x, env):
    #if debug: print "seval x=%r" % (x,)

    if type(x)==str:
        return env[x]
    if not isinstance(x, tuple):
        return x

    #>>> it's a list, special forms
    h = x[0]
    if h=='quote': return x[1]
    if h=='if': return evalIf(x, env)
    if h=='def':
        var = x[1]; value = seval(x[2], env)
        env.define(var, value)
        return value
    if h=='set!':
        var = x[1]; value = seval(x[2], env)
        env.getEnvFor(var).define(var, value)
        return value
    if h=='begin':
        for ex in x[1:]:
            value = seval(ex, env)
        return value
    if h=='fn':
        args = x[1]; body = x[2]
        return Closure(args, body, env)
    if h=='eval':
        return seval(seval(x[1], env), env)

    #>>> it's a list, evaluate arguments and run it
    evaled = [seval(arg, env) for arg in x]
    return evaled[0](*evaled[1:])

def evalIf(x, env):
    """ evaluate an if, which is of the form:
    (if con1 ex1
        con2 ex2
        ...
        con_n ex_n)
    An alternate form is without the ex_n, in which case
    the result of con_n is returned.
    """
    if debug: print "evalCond %s" % (spilltypes.show(x),)
    current = 1
    while True:
        lastEval = seval(x[current], env)
        if spillTrue(lastEval)=='true':
            if debug: print "evalCond() current=%r" % current
            return seval(x[current+1], env)
        current += 2
        if current+1 == len(x):
            return seval(x[current], env)
        if current == len(x):
            return lastEval
    #//while

#---------------------------------------------------------------------
# big system object

class SpillSys:
    def __init__(self):
        self.globalEnv = Environment()
        addPrimitivesToEnv(self.globalEnv)
        self.parser = parser.SpillParser()
        self.lastResult = None
        self.loadFile("libcore.l")

    #@printargs
    def readEval(self, evalStr):
        """ Read and evaluate a string. Return the result.
        @param evalStr [str] containing an s-expression to be parsed
           and run.
        @return [s-exp] the result
        """
        tokens = lexer.Lexer().tokenize(evalStr)
        self.parser.parse(tokens, self.evalResultFromParsing)
        return self.lastResult

    def eval(self, ex):
        """ evaluate an s-expression, using the global environment """
        return seval(ex, self.globalEnv)

    #@printargs
    def evalResultFromParsing(self, result):
        expanded = self.macroExpand(result)
        self.lastResult = seval(expanded, self.globalEnv)

    def loadFile(self, filename):
        if debug: print "loading <%s>" % (filename,)
        fileContents = butil.readFile(filename)
        self.readEval(fileContents)

    def macroExpand(self, ex):
        ex2 = self.macroExpand2(ex)
        if debug and ex2!=ex:
           print "macro expansion %s --> %s" % (spilltypes.show(ex),
              spilltypes.show(ex2))
        return ex2


    def macroExpand2(self, ex):
        """ perform macro expansion """
        #print "macroExpand2() ex=%r" % (ex,)
        if not isinstance(ex, tuple) or len(ex)==0: return ex
        #print "macroExpand2()"
        h = ex[0]
        #print "macroExpand2() h=%r" % (h,)
        if h == 'quote': return ex
        elif h == 'quasiquote': return expandQuasi(ex[1])
        elif self.isMacro(h):
            #print "expanding ex=%r" % (ex,)
            expanded = self.expandAMacro(h, ex)
            #print "macroExpand2() expanded=%r" % (expanded,)
            return self.macroExpand2(expanded)
        else:
            return tuple([self.macroExpand2(e) for e in ex])


    def isMacro(self, sym):
        return self.globalEnv.data.has_key("macro~" + sym)

    def expandAMacro(self, h, ex):
        macroFunction = self.globalEnv["macro~" + h]
        return macroFunction(*ex[1:])

def expandQuasi(ex):
    """ expand an expression in quasi-quotes
    `  = quasi                  `x => 'x
    ,  = unquote                `,x => x
    '@ = unquotesplicing (uqs)  `(x ,@y z) =>

    """
    if not isPair(ex):
        return ('quote', ex)
    h = ex[0]
    require(ex, h!='unquotesplicing', "can't splice here")
    if h == 'unquote':
        require(ex, len(ex)==2)
        return ex[1]
    elif isPair(h) and h[0]=='unquotesplicing':
        require(h, len(h)==2)
        return ('append', h[1], expandQuasi(ex[1:]))
    else:
        return ('cons', expandQuasi(h), expandQuasi(ex[1:]))

def require(self, predicate, message=""):
    "Signal a syntax error if predicate is false."
    if not predicate:
        raise SyntaxError(spilltypes.show(x) + ': ' + message)

#---------------------------------------------------------------------
# if called as __main__


if __name__=='__main__':
    #print "Welcome to Spill, args=%r" % (sys.argv,)
    si = SpillSys()
    for arg in sys.argv[1:]:
        si.loadFile(arg)





#end
