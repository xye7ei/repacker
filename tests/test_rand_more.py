import preamble
import random
import gc
from pprint import pprint
from repacker import *

for _ in range(100):

    s = Scene(100000, 100000)

    rs = [Rectangle(random.randint(10, 50),
                    random.randint(10, 50))
        for _ in range(500)
    ]

    # rs.sort(key=lambda r: (r.area, r.b), reverse=True)

    s.prepare(rs)
    s.plan(rs)

    gc.collect()

    # BUGS:


# show(rs)
# figure(rs)
