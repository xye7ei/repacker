#!/usr/bin/env python3

import preamble

import random
from pprint import pprint
from repacker import *

s = Scene(100000, 100000)

# rs = [Rectangle(random.randint(10, 100),
#                 random.randint(10, 100))
#     for _ in range(500)
# ]

rs = [Rectangle(random.randint(1, 100),
                random.randint(1, 100))
    for _ in range(500)
]

rs.extend(
    Rectangle(33, 33)
    for _ in range(50)
)

rs.extend(
    Rectangle(66, 66)
    for _ in range(50)
)

rs.sort(key=lambda r: (r.area, r.b), reverse=True)
# rs.sort(key=lambda r: (r.area, r.b + r.h), reverse=True)

s.prepare(rs)
rate = s.plan()

print(rate)

# BUGS:
# - Dead loop
# - Accessing attributes of None
# - Accessing attributes of None

show(s)
# s.figure()

# under Linux, use
# time python3 xxx
# to read the execution time.
