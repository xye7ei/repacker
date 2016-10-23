import preamble

from repacker import *

from unittest import TestCase, main

# Plan:
# n0: (0, 0)

rs = [
    Rectangle(30, 5),
    # (30, 5) @ n0
    # n1: (0, 5)
    # n2: (30, 0)

    Rectangle(10, 30),
    # (10, 30) @ n1
    # n3: (0, 35)
    # n4: (10, 5)

    Rectangle(30, 5),
    # (30, 5) @ n3
    # n5: (0, 40)
    # n6: (30, 35)

    Rectangle(5, 37),
    # (5, 37) @ n2
    # n7: (30, 37)
    # n8: (35, 0)

    Rectangle(10, 10)
    # (10, 10) @ n7  - ! align to n6 as plant
    # n9: (30, 47)
    # n9: (40, 37)
]


# class Test(TestCase):

#     def test(self):

x_max = 50
y_max = 50

s = Scene(x_max, y_max)
top = s.top
o = top.next
n1, n2 = o.plant(rs[0])
assert (n1.x, n1.y) == (0, 5)
assert (n2.x, n2.y) == (30, 0)
assert n1.left == n1, n1.left
assert n1.right == top
assert n1.up == top
assert n1.down == n1
assert n2.left == n2, n2.left
assert n2.right == top
assert n2.up == top
assert n2.down == n2
assert top.next == n1
assert n1.next == n2
assert n2.next == top

n3, n4 = n1.plant(rs[1])
assert (n3.x, n3.y) == (0, 35)
assert (n4.x, n4.y) == (10, 5)
assert n3.up == top
assert n3.right == top
assert n3.down == n3
assert n3.left == n3
assert n4.up == top
assert n4.right == top
assert n4.down == n4
assert n4.left == n4

n5, n6 = n3.plant(rs[2])
assert (n5.x, n5.y) == (0, 40)
assert (n6.x, n6.y) == (30, 35)
assert n5.up == top
assert n5.right == top
assert n5.down == n5
assert n5.left == n5
assert n6.left == n6
assert n6.right == top
assert n6.up == top
assert n6.x == n2.x
assert n6.down == n2.prev
assert n6.down == n4            # n6.x == n4.x

# merging this rect
n7, n8 = n2.plant(rs[3])
assert n4.next == n7
assert n7.prev == n4
assert n7.next == n8
assert n8.prev == n7
assert n8.next == top
assert top.prev == n8

assert n7.xy == (30, 37)
assert n8.xy == (35, 0)
assert n7.left == n6
assert n7.right == top
assert n7.up == top
assert n7.down == n7
assert n8.left == n8.down == n8, (n8.left, n8.down)
assert n8.up == n8.right == top

n9, n10 = n7.plant(rs[4])
assert n9.xy == (30, 47)
assert n10.xy == (40, 37)
assert n5.next == n9
assert n9.prev == n5
assert n9.next == n10
assert n10.prev == n9
assert n10.next == n6
assert n6.prev == n10

assert n5.right == n9
assert n9.left == n5
assert n9.right == top
assert n9.up == top
assert n9.down == n9
assert n10.left == n10
assert n10.down == n8
assert n10.up == top, n10.up
assert n10.right == top, n10.right

assert n6.up == n10
assert n6.right == n7
assert n6.down == n4
assert n6.left == n6
assert n4.up == n6
assert n4.right == n7
assert n7.left == n6
assert n7.up == n10
assert n7.right == top
assert n7.down == n7
assert n8.up == n10
assert n8.right == top

assert list(top.walk()) == [top, n5, n9, n10, n6, n4, n7, n8]

# if __name__ == '__main__':
#     main()
# show(rs)
