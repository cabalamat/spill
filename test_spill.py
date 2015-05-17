# test_spill.py = test the Spill system


import addpath
import lintest

import parser
import spilltypes
import spill


#---------------------------------------------------------------------

class SpillTestTools(lintest.TestCase):

    def setUp(self):
        self.si = spill.SpillSys()

    def assertSameSpill(self, rData, sbData, comment=""):
        self.assertEqual(spilltypes.show(rData),
                         spilltypes.show(sbData),
                         comment)

    def retr(self, evalStr, sbStr, optComment=""):
        """ Read and Evaluate an expression, then Test the Result.
        @param evalStr [str] = expression to be parsed and evaluated
        @param sbStr [str] = what the show-form of the result should be
        """
        result = self.si.readEval(evalStr)
        resultStr = spilltypes.show(result)
        sbData = parser.parseExp(sbStr)
        comment = "testing %s => %s" % (evalStr, sbStr)
        if optComment: comment += "; " + optComment
        if result == sbData:
            self.passedTest(comment)
        else:
            self.failed("%s result=%s sb=%s" % (comment, result, sbData))

#---------------------------------------------------------------------

class T_parser(lintest.TestCase):
    def parseExp(self, expStr, sb, optComment=""):
        r = parser.parseExp(expStr)
        self.assertSame(r, sb, "parse {%s} "%(expStr,) + optComment)

    def test_atoms(self):
        #>>>>> numbers
        self.parseExp("34", 34, "the number 34")
        self.parseExp("-9", -9)
        self.parseExp("123456789", 123456789)

        #>>>>> identifiers
        self.parseExp("theWay", 'theWay')
        self.parseExp("+", '+')

        #>>>>> strings
        self.parseExp('"a string"', spilltypes.LStr("a string"))
        self.parseExp(' "" ', spilltypes.LStr(""))

    def test_lists(self):
        self.parseExp(" () ", ())
        self.parseExp(" (1) ", (1,))
        self.parseExp(" (1 2) ", (1,2))
        self.parseExp(" (1  2   longIdentifier) ",
                        (1, 2, 'longIdentifier'))
        self.parseExp(" (1 2 (a b c)        (x)    ()) ",
                        (1,2,('a','b','c'), ('x',),()) )

    def test_quote(self):
        self.parseExp(" '() ", ('quote', ()))
        self.parseExp(" '3 ", ('quote', 3))
        self.parseExp(" 'abc ", ('quote', 'abc'))
        self.parseExp(""" '"abc" """, ('quote', spilltypes.LStr("abc")))
        self.parseExp("'''x", ('quote',('quote',('quote', 'x'))))

    def test_quasiquoting(self):
        self.parseExp(" `(x y) ", ('quasiquote', ('x', 'y'))    )
        self.parseExp(" ,x ", ('unquote', 'x')    )
        self.parseExp(" ,@x ", ('unquotesplicing', 'x')    )

#---------------------------------------------------------------------

class T_spilltypes(SpillTestTools):

    def test_exToList(self):
        data = (1, 2, 3)
        r = spilltypes.exToList(data)
        sb = [1,2,3]
        self.assertSame(r, sb, "convert tuple to list")

        r = spilltypes.exToList( () )
        self.assertSame(r, [], "empty list")

        r = spilltypes.exToList( ('fn', ('a', 'b'), ('*', 'a', 'b')) )
        sb = ['fn', ['a', 'b'], ['*', 'a', 'b']]
        self.assertSame(r, sb, "nested list")

#---------------------------------------------------------------------

class T_basicFunctionality(SpillTestTools):


    def test_1(self):
        self.retr("(+ 4 5)", "9")
        self.retr("'(+ 4 5)", "(+ 4 5)")

    def test_listFunctions(self):
        self.retr("(cons 'a '(b c))", "(a b c)")
        self.retr("(cons 5 '(b c))", "(5 b c)")
        self.retr("(cons 5 '())", "(5)")
        self.retr("(append '(x) '(y) '(3))", "(x y 3)")

    def test_square(self):
        self.retr("""
        (def square (fn (x) (* x x)))
        (square 9)
        """, "81")

    def test_varargs(self):
        self.retr("""
        (def foo (fn (* args)
           args))
        (foo 1 '(xx yy) 3)
        """, "(1 (xx yy) 3)")

        self.retr("""
        (def xx '(this is a list))
        (foo 1 xx 3)
        """, "(1 (this is a list) 3)")

    def test_comparisons(self):
        self.retr("(< 1 2)", "true")
        self.retr("(< 1 -2)", "false")
        self.retr("(> 1 2)", "false")
        self.retr("(> 1 -2)", "true")
        self.retr("(== -2 -2)", "true")
        self.retr("(== 1 -2)", "false")
        self.retr("(== '(a b c) '(a b c))", "true")
        self.retr("(== '(a b c) '(a b d))", "false")

    def test_eval(self):
        self.retr("(eval '(+ 2 5))", "7")
        self.retr("""
        (def foo (fn ()
            (begin
                (def bar 5)
                (def baz 6)
                (eval '(+ bar baz)))))
        (foo)
        """, "11")


#---------------------------------------------------------------------

class T_libcore(SpillTestTools):
    """ test the function in libcore.l """

    def test_map(self):
        self.retr("""
        (def square (fn (x) (* x x)))
        (map square '(1 2 3 4 5))
        """, "(1 4 9 16 25)")

    def test_filter(self):
        self.retr("""
        (def filter (fn (f a)
            (if (null? a)      '()
                (f (car a))    (cons (car a) (filter f (cdr a)))
                'true          (filter f (cdr a)))))

        (def mod (fn (a b) ;a - (a/b)*b
            (- a (* (/ a b) b))))

        (def odd? (fn (n) (eq? (mod n 2) 1)))

        (filter odd? '(1 2 3 4 5 6 7 8 9 10))
        """, "(1 3 5 7 9)")

    def test_listFunctions(self):
        self.retr("""(list 3 6 '(a b) "c")""", """(3 6 (a b) "c")""")
        self.retr("""
        (def foo '(1 45))
        (def bar '(baa baa baa))
        (list foo bar)""", """((1 45) (baa baa baa))""")
        self.retr("(fromto 1 5)", "(1 2 3 4 5)")
        self.retr("(fromto -6 -6)", "(-6)")
        self.retr("(fromto 6 5)", "()")

    def xtest_miscFunctions(self):
        self.retr("(and 'foo 'bar)", "(if (not foo) 'false bar)")

#---------------------------------------------------------------------


class T_macros(SpillTestTools):
    """ test macro expansion """

    def macExpand(self, inputStr, sbOutputStr):
        ex = parser.parseExp(inputStr)
        expanded = self.si.macroExpand(ex)
        print "expanded: %s" % (spilltypes.showStr(expanded),)
        r = self.si.eval(expanded)
        sbData = parser.parseExp(sbOutputStr)
        self.assertSameSpill(r, sbData,
           "macro-expansion of " + inputStr)

    def test_macroExpansion(self):
        ex = parser.parseExp("(and foo bar)")
        r = self.si.macroExpand(ex)
        self.assertSameSpill(r,
           parser.parseExp("(if (not foo) 'false bar)"))


    def test_quasiquote(self):
        # we need this in some macro-expansions
        self.si.readEval("(def b '(33 44))")

        #   `x => 'x
        self.macExpand("(quasiquote x)", "x")

        #   `(a b c) => '(a b c)
        self.macExpand("(quasiquote (a b c))", "(a b c)")

        #   `(a ,b c) => (list 'a b 'c)
        self.macExpand("(quasiquote (a (unquote b) c))", "(a (33 44) c)")

        #   `(a ,@b c) => (cat '(a) b '(c))
        self.macExpand("(quasiquote (a (unquotesplicing b) c))", "(a 33 44 c)")

    def test_quasiquote2(self):
        # as above, but use appreviations
        self.si.readEval("(def b '(33 44))")
        self.macExpand("`x", "x")
        self.macExpand("`(a b c)", "(a b c)")
        self.macExpand("`(a ,b c)", "(a (33 44) c)")
        self.macExpand("`(a ,@b c)", "(a 33 44 c)")

    def test_macros(self):
        " now let's build some actual macros and test them "
        r = self.si.readEval("""
        (def macro~or (fn (a b)
            `(if ,a 'true ,b)))
        """)
        print r
        r = self.si.readEval("""
        (def t 'true) (def u 'false)
        (def v (or t u))
        """)
        print r

    def test_macros_or2(self):
        r = self.si.readEval("""
        (def macro~or2 (fn (* args)
            `(if ,a 'true ,b)))
        """)

#---------------------------------------------------------------------

group = lintest.TestGroup()
group.add(T_parser)
group.add(T_spilltypes)
group.add(T_basicFunctionality)
group.add(T_libcore)
group.add(T_macros)

if __name__=="__main__": group.run()



#end
