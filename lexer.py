# lexer.py = a lexical analyser for Spill

import string

import addpath
import istream

debug=0

#---------------------------------------------------------------------

class MatchedSymbolEx(Exception):
    """ this gets called when we've matched a symbol """

class PosToken:
    def __init__(self, type, attr=None, line=0, col=0):
        self.type = type
        self.attr = attr
        self.line = line
        self.col = col

    def __cmp__(self, o):
        return cmp(self.type, o)

    def __repr__(self):
        x = "%r" % (self.type,)
        if self.attr != None:
            x = "(%s %r)" % (self.type, self.attr)

        if self.line > 0:
            x = x + (':%s:%s' %(self.line, self.col))
        return x

HEX_TO_DEC = {
   '0':0, '1':1, '2':2, '3':3, '4':4,
   '5':5, '6':6, '7':7, '8':8, '9':9,
   'a':10, 'A':10,
   'b':11, 'B':11,
   'c':12, 'C':12,
   'd':13, 'D':13,
   'e':14, 'E':14,
   'f':15, 'F':15,
}

def replaceStringEscapes(s):
    r""" replace Spill escapes in a string. Spill escapes are:

    ESCAPE   REWRITES-TO
      \'       '     (single-quote, ascii 39)
      \n             (newline, ascii 10)
      \\       \     (backslash, ascii 92)
      \xnn           any ascii character 1..127 n is a hex digit

    @param s [string] = a literal for a Unify string, minus the
       single-quotes that normally go at begining and end
    @return [string] the same string with unify excapes rewritten
    """
    if debug:
        print "replaceStringEscapes(s=%r)" % (s,)
    r = ""
    ix = 0
    while 1:
        if ix >= len(s): break
        c = s[ix]
        if c!="\\":
            r += c
            ix += 1
            continue
        if ix+1>=len(s): break
        ix += 1
        c = s[ix]
        if c=="n":
            r += "\n"
            ix += 1
            continue
        if c=="\\":
            r += "\\"
            ix += 1
            continue
        if c=="x":
            if ix+2>=len(s): break
            hex1d = s[ix+1]
            hex2d = s[ix+2]
            ix += 3
            try:
                ascValue = HEX_TO_DEC[hex1d]*16 + HEX_TO_DEC[hex2d]
                r += chr(ascValue)
            except:
                continue
    #//while
    return r

#---------------------------------------------------------------------

IDENT_START_CHAR = string.ascii_letters + "_~?!+-*/<>="
IDENT_CHAR = IDENT_START_CHAR + "0123456789"

#---------------------------------------------------------------------

class Lexer:

    def __init__(self):
        self.rv = []

    def tokenize(self, s):
        """ Tokenize a string
        @param s [string]
        @return [list of PosToken]
        """
        self.rv = []
        self.ss = istream.ScanString(s)
        self.lex()
        return self.rv

    def addToken(self, tokenType, tokenValue=None):
        if debug: print "addToken(%s, %r)" % (tokenType, tokenValue)
        line,col = self.ss.getLocation()
        token = PosToken(tokenType, tokenValue, line, col)
        self.rv.append(token)

    def lex(self):
        if debug: print "lex()"
        while not self.ss.eof():
            try:
                self.lex1()
            except MatchedSymbolEx:
                pass

    #========================================================

    def lex1(self):
        ss = self.ss

        if ss.skipPastSet(" \t\n"): return

        # ;{{...;}} multi-line comments
        if ss.isNextSkip(";{{"):
            ss.skipPast(";}}")
            return

        # #|...|# multi-line comments
        if ss.isNextSkip("#|"):
            ss.skipPast("|#")
            return

        # ;... comments
        if ss.isNextSkip(";"):
            ss.skipPast("\n")
            return

        if ss.isNextInt():
            self.addToken('INTEGER', ss.grabInt())
            return

        if ss.isNextWord(IDENT_START_CHAR):
            s = ss.grabWord(IDENT_START_CHAR, IDENT_CHAR)
            self.addToken('IDENTIFIER', s)
            return

        if ss.isNext('"'):
            # it's a string
            s = ss.get()
            while 1:
                ch = ss.get()
                if ch=='': break
                s += ch
                if ch=='"': break
                if ch=='\\': s += ss.get()
            #//while
            s2 = s[1:-1]
            #s3 = string.replace(s2, r"\'", "'")
            #s3 = string.replace(s3, r"\n", "\n")
            #s3 = string.replace(s3, r"\\", "\\")

            s3 = replaceStringEscapes(s[1:-1])
            self.addToken('STRING', s3)
            return

        self.tryMatch("'", 'QUOTE')
        self.tryMatch("`", 'QUASIQUOTE')
        self.tryMatch(",@", 'UNQUOTESPLICING')
        self.tryMatch(",", 'UNQUOTE')
        self.tryMatch("(")
        self.tryMatch(")")

        #couldn't do anything else, so consume one character
        if not ss.eof():
            self.addToken(ss.getChar())

    #========================================================

    def tryMatch(self, matchStr, tokenType=None, tokenValue=None):
        if self.ss.isNextSkip(matchStr):
            if tokenType==None: tokenType = matchStr
            self.addToken(tokenType, tokenValue)
            raise MatchedSymbolEx

#---------------------------------------------------------------------

def testMe():
    print "--- test lexer ---"
    s = """hello world
    ; this is a comment
    ( 1234 `(a ,b c ,@d e) ()
    """
    scanner = Lexer()
    res = scanner.tokenize(s)
    print "res=%r" % (res,)
    for tok in res:
        print "%r" % (tok,)


if __name__=='__main__':
    testMe()

#end
