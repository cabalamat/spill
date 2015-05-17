# parser.py = parser for Spill

import string

import addpath
import spark07; spark = spark07 # SPARK parsing framework

import lexer
import spilltypes

debug = 0

#---------------------------------------------------------------------
# exceptions for parsing errors

class SpillSyntaxError(Exception):
    """ an error occurred while parsing Spill code or literals """


# debugging:
def sayWhere(info):
    if debug:
        import traceback
        fromFun = traceback.extract_stack()[-2]
        print ">>> %s() %r" %(fromFun[2], info)

#---------------------------------------------------------------------

"""***
SpillParser is a parser for Spill
***"""

class SpillParser(spark.GenericParser):

    def __init__(self, startSymbol=None):
        if startSymbol==None: startSymbol = 'sourceFile'
        spark.GenericParser.__init__(self, startSymbol)

    def parse(self, tokenList, callbackFun=None):
        if callbackFun==None:
            self.callback = lambda x: x
        else:
            self.callback = callbackFun
        result = spark.GenericParser.parse(self, tokenList)
        return result

    def p_sourceFile(self, args):
        """
        sourceFile ::=
        sourceFile ::= sourceFile exp
        """
        sayWhere(args)
        if len(args)==2:
            self.callback(args[1])

    def p_exp_0n(self, args):
        """
        exp_0n ::=
        exp_0n ::= exp exp_0n
        """
        sayWhere(args)
        if len(args)==2:
            cdr = args[1]
            if cdr==None: cdr = ()
            retval = tuple([args[0]] + list(cdr))
            return retval

    def p_exp_list(self, args):
        """ exp ::= ( exp_0n ) """
        sayWhere(args)
        if args[1]==None: return ()
        return args[1]

    def p_exp_atoms(self, args):
        """
        exp ::= INTEGER
        exp ::= IDENTIFIER
        exp ::= STRING
        """
        sayWhere(args)
        if args[0].type=='STRING':
            return spilltypes.LStr(args[0].attr)
        else:
            # it's an integer or identifier
            return args[0].attr

    def p_exp_quote(self, args):
        """ exp ::= QUOTE exp """
        sayWhere(args)
        return ('quote', args[1])

    def p_exp_quasiquote(self, args):
        """ exp ::= QUASIQUOTE exp """
        sayWhere(args)
        return ('quasiquote', args[1])

    def p_exp_unquote(self, args):
        """ exp ::= UNQUOTE IDENTIFIER """
        sayWhere(args)
        return ('unquote', args[1].attr)

    def p_exp_unquotesplicing(self, args):
        """ exp ::= UNQUOTESPLICING IDENTIFIER """
        sayWhere(args)
        return ('unquotesplicing', args[1].attr)


#---------------------------------------------------------------------

expressionParser = SpillParser('exp')

def parseExp(expStr):
    """ parse an expression """
    tokens = lexer.Lexer().tokenize(expStr)
    return expressionParser.parse(tokens)


#---------------------------------------------------------------------
# testing


def test_parser():
    print "--- test parser: lexer ---"
    s = '''(str1 "string 2" 50 (in) x () '() y zz)'''
    scanner = lexer.Lexer()
    tokenList = scanner.tokenize(s)
    print "--- results from scanner:"
    for tok in tokenList:
        print "%r" % (tok,)

    parser = SpillParser()
    ar = parser.parse(tokenList)
    print "--- from parser: ar = %r" % (ar,)


#---------------------------------------------------------------------

if __name__=="__main__":
    #test_lexer()
    test_parser()
















#end
