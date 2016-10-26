import preamble
from repacker import *

s = Scene(50, 50)
top = s.top

rs = [
    Rectangle(5, 5),
    Rectangle(10, 10),
    Rectangle(7, 7),
]

s.prepare(rs)

n1, n2 = s.top.next.plant(rs[0])
n3, n4 = n1.plant(rs[1])

# BUGGY:
n5, n6 = n4.plant(rs[2])

s.validate_linking()
show(s)
