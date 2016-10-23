import random
from pprint import pprint
from repacker import *

s = Scene(100000, 100000)

rs = [Rectangle(random.randint(10, 50),
                random.randint(10, 50))
    for _ in range(300)
]

rs.extend(
    Rectangle(20, 20)
    for _ in range(30)
)

rs.extend(
    Rectangle(35, 35)
    for _ in range(30)
)

# rs.sort(key=lambda r: (r.area, r.b), reverse=True)
rs.sort(key=lambda r: (r.area, r.b + r.h), reverse=True)

s.plan(rs)

# BUGS:
# - Dead loop
# - Accessing attributes of None
# - Accessing attributes of None

show(rs)
# figure(rs)
