import preamble
from repacker import *

from unittest import TestCase, main

rs = []

for i in range(1, 15):
    rs += [
        Rectangle(i, i)
        for _ in range(30)
    ]


s = Scene(10000, 10000)
top = s.top
ori = top.next

s.prepare(rs)

rate = s.plan()

print(rate)

show(s)
