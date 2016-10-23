from test_align_merge import *

# show(rs)

assert n5.estm_slot_size() == (n9.x - n5.x) * (y_max - n5.y)
assert n9.estm_slot_size() == (x_max) * (y_max - n9.y)
assert n10.estm_slot_size() == (x_max - n10.x) * (y_max)
assert n4.estm_slot_size() == (n7.x - n4.x) * (n6.y - n4.y)
assert n6.estm_slot_size() == 0
assert n7.estm_slot_size() == 0
assert n8.estm_slot_size() == (x_max - n8.x) * (n10.y)

rs.append(Rectangle(5, 5))

assert n10.xy == (40, 37)
assert n8.up == n10


n11, n12 = n8.merge(rs[-1])

# show(rs)

assert n10.down == n11, n10.down
assert n11.xy == (35, 5)
assert n12.xy == (40, 0)
assert n11.up == n10
assert n11.right == top
assert n12.up == top, n12.up
assert n12.right == top
assert n12.left == n12
assert n12.down == n12


rs.append(Rectangle(5, 5))
r_last = rs[-1]

assert n11.slot_fill_rate(r_last) == 25 / (x_max - n8.x) / (n10.y - n11.y) 
assert n12.slot_fill_rate(r_last) == 25 / (x_max - n10.x) / (y_max)
