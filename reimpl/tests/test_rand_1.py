#!/usr/bin/env python3

import preamble

import random
from pprint import pprint
from repacker import *

s = Scene(100000, 100000)

rs = [Rectangle(random.randint(10, 100),
                random.randint(10, 100))
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

s.plan(rs)

# BUGS:
# - Dead loop
# - Accessing attributes of None
# - Accessing attributes of None

show(rs)
# figure(rs)

# under Linux, use
# time python3 xxx
# to read the execution time.
