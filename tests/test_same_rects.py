import preamble
from repacker import *

from unittest import TestCase, main

# Plan:

# n0: (0, 0)

rs = [
    Rectangle(5, 5)
    for _ in range(30)
]


# class Test(TestCase):

#     def test(self):

s = Scene(10000, 10000)
top = s.top
ori = top.next

s.prepare(rs)

# for r in rs:
#     n = s.walk_find_best(r)
#     n.plant(r)

s.plan()

# if __name__ == '__main__':
#     main()

show(s)
