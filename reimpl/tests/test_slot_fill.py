from repacker import *

xm = ym = 100

R = Rectangle
rs = [
    R(10, 10),
    R(10, 10),
    R(10, 10),
    R(10, 10),
    R(10, 10),
    R(10, 10),
    R(10, 10),
    R(10, 10),
]


s = Scene(xm, ym)
top = s.top
n0 = top.next


n1, n2 = n0.plant(rs[0])
n3, n4 = n1.plant(rs[1])

assert n3.next == n4
assert n4.next == n2
assert n2.next == top
assert n4.up == top
assert n4.right == top
assert n4.left == n4
assert n4.down == n4
assert n4.slot() == (90, 90)
assert n2.up == top

n5, n6 = n2.plant(rs[2])
assert n5.up == top
assert n5.right == top
assert n5.left == n5
assert n5.down == n5
assert n4.next == n5

assert n5.can_plant(rs[3])
n7, n8 = n5.plant(rs[3])
assert n7 == n4.next
assert n8 == n7.next
assert n7.left == n4
assert n7.down == n7
assert n7.up == n7.right == top
assert n3.right == top
assert n4.right == n7
assert n4.slot() == (0, 90)

assert n7.slot() == (90, 80)
assert n7.can_plant(rs[4])
assert n8.can_plant(rs[4])
assert n8.slot() == (80, 90)

show(rs)
