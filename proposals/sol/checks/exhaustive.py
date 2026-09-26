#!/usr/bin/env python3
from itertools import product

Z = (0, 1, 2)
ACTIONS = (0, 1)  # 0=stay, 1=advance

def read(z):
    return "A" if z in (0, 1) else "B"

def step(z, a):
    assert z in Z
    assert a in ACTIONS
    return (z + a) % 3

def run(z, word):
    traj = [z]
    for a in word:
        z = step(z, a)
        traj.append(z)
    return z, tuple(traj)

# A
z, zp = 0, 1
assert z != zp
assert read(z) == read(zp) == "A"

# B: same operation reveals the same preserved state difference
assert (zp - z) % 3 == 1
bz = step(z, 1)
bzp = step(zp, 1)
assert (bzp - bz) % 3 == 1
assert read(bz) != read(bzp)

# C: observed return, full-state update, then same continuation reveals it
returned = step(0, 1)
assert returned != 0
assert read(returned) == read(0)
assert read(step(returned, 1)) != read(step(0, 1))

# Full-state advance cycle has period 3
x = 0
cycle = [x]
for _ in range(3):
    x = step(x, 1)
    cycle.append(x)
assert cycle == [0, 1, 2, 0]

# D: same start, fixed horizon 3, terminal readout A
def constraint(word):
    if len(word) != 3:
        return False
    end, _ = run(0, word)
    return read(end) == "A"

alpha = (0, 1, 0)
beta = (1, 1, 1)
gamma = (0, 1, 1)

end_a, traj_a = run(0, alpha)
end_b, traj_b = run(0, beta)
end_g, traj_g = run(0, gamma)

assert constraint(alpha)
assert constraint(beta)
assert not constraint(gamma)
assert traj_a != traj_b
assert end_a != end_b
assert read(end_a) == read(end_b) == "A"

# Same continuation reveals the distinct allowed histories
assert read(step(end_a, 1)) != read(step(end_b, 1))

# Enumerate all horizon-3 words
rows = []
for w in product(ACTIONS, repeat=3):
    end, traj = run(0, w)
    rows.append((w, traj, end, read(end), constraint(w)))

print("A-D checks: PASS")
print("advance cycle:", cycle)
print("horizon-3 paths from state 0:")
for row in rows:
    print(row)
