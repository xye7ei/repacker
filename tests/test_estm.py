import preamble
from repacker import *

s = Scene(100, 100)
rs = []

rs += [Rectangle(2, 5)]

n = s.walk_find_best(rs[0])

n1, n2 = n.plant(rs[0])

# show(rs)

rs += [Rectangle(1, 5)]
n = s.walk_find_best(rs[1])
n3, n4 = n.plant(rs[1])

# show(rs)

rs += [Rectangle(2, 10)]
n = s.walk_find_best(rs[2])
n5, n6 = n.plant(rs[2])

s.prepare(rs)

show(s)

