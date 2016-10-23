from repacker import *

s = Scene(100, 100)
rs = []

rs += [Rectangle(2, 5)]

n = s.walk_find_best(rs[0])

n1, n2 = n.merge(rs[0])

# show(rs)

rs += [Rectangle(1, 5)]
n = s.walk_find_best(rs[1])
n3, n4 = n.merge(rs[1])

# show(rs)

rs += [Rectangle(2, 10)]
n = s.walk_find_best(rs[2])
n5, n6 = n.merge(rs[2])

show(rs)

