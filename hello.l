; hello.l

(pr "Hello, world!\n")

;(pr (fromto 1 10))

;(def odd-to-20 (filter odd? (fromto 1 10)))
;(pr "Odd numbers to to 20: " odd-to-20 "\n")

(def addn (fn (n)
   (fn (x) (+ n x))))

(def foo (addn 3))

(pr '(foo 10) " => " (foo 10))

(pr (fromto 1 10))

(pr "\nmacro~and: " (macro~and 2 3))

(pr "\nsquares: "
   (map (fn (x) (* x x))
        (fromto 1 10)))

(pr "\n\n")



;end