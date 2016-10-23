from repacker import *

s = Scene(50, 50)
top = s.top
ori = top.next

rs = [
    Rectangle(5, 5),
    Rectangle(10, 10),
    Rectangle(7, 7),
]

n1, n2 = ori.merge(rs[0])
n3, n4 = n1.merge(rs[1])

# BUGGY:
n5, n6 = n4.merge(rs[2])

s.validate_linking()
show(rs)
