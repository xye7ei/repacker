import preamble
import random
import gc
from pprint import pprint
from repacker import *

# for _ in range(100):
for _ in range(1):

    s = Scene(100000, 100000)

    rs = [Rectangle(random.randint(10, 50),
                    random.randint(10, 50))
        for _ in range(1000)
    ]

    # rs.sort(key=lambda r: (r.area, r.b), reverse=True)

    s.prepare(rs)
    rho = s.plan()

    print(rho)

    gc.collect()

    # BUGS:


show(s)
# figure(rs)
