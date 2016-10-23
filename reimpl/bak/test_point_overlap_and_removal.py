from repacker import *

from unittest import TestCase, main

# Plan:

# n0: (0, 0)
R = Rectangle

rs = [
    R(1, 3), 
    R(3, 1), 
    R(5, 1), 
    R(7, 1), 
    R(3, 1), 
    R(2, 1), 
]

# class Test(TestCase):

#     def test(self):

s = Scene(50, 50)
top = s.top
ori = top.next

n = [ori]

n += ori.merge(rs[0])
n += n[1].merge(rs[1])
n += n[3].merge(rs[2])
n += n[5].merge(rs[3])
n += n[2].merge(rs[4])

assert n[4].down == n[9]
assert n[6].down == n[10]
assert n[8].down == n[10]

n += n[10].merge(rs[5])

# Spontaneous n11 is dropped.
assert n[11] is n[9]
assert n[11].next is n[12]
assert n[11].up == n[4]

assert n[4].down == n[9]
assert n[6].down == n[9], n[6].down # 
assert n[8].down == n[12], n[8].down
assert n[8].down == n[9].next

# if __name__ == '__main__':
#     main()

show(rs)
