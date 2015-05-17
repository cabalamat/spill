; libcore.l

#|
libcore is spill's standard library.
|#

;---------------------------------------------------------------------
#| list functions |#

; perform f on each element of a. Collect the results.
(def map (fn (f a)
    (if (null? a) '()
        (cons (f (car a))
              (map f (cdr a))))))

; return those parts of a for which f is true.
(def filter (fn (f a)
   (if (null? a)      '()
       (f (car a))    (cons (car a) (filter f (cdr a)))
       'true          (filter f (cdr a)))))


; make a list out of my args
(def list (fn (* args) args))

; make a list f..t
(def fromto (fn (f t)
   (if (> f t) '()
       (cons f (fromto (+ f 1) t)))))


;---------------------------------------------------------------------
#| misc functions |#

(def not (fn (b)
   (if b 'false 'true)))

;---------------------------------------------------------------------
#| maths functions |#

(def mod (fn (a b) ;a - (a/b)*b
   (- a (* (/ a b) b))))

(def odd? (fn (n) (eq? (mod n 2) 1)))
(def even? (fn (n) (eq? (mod n 2) 0)))

;---------------------------------------------------------------------
#|  macros

(and a b) => (if (not a) 'false
                 b)
|#

(def macro~and (fn (a b)
   (list 'if
      (list 'not a)
      ''false
      b)))
(def and macro~and)

(def macro~and2 (fn (a b)
   `(if (not ,a) 'false ,b)))

(def macro~defn (fn (name args * body)
   `(def ,name (fn ,args ,@body))))

(defn plus3 (n) (+ n 3))

;---------------------------------------------------------------------


;end
