"""Exact arithmetic checks for the local contact candidate, not future causality."""
from fractions import Fraction as Q
from itertools import product
import json


def rho(z):
    a, b, r = z
    return a + r * b


def velocity(z, demand, free):
    a, b, r = z
    return (demand - r * free, r * demand + free, b * demand)


def drho(z, w):
    a, b, r = z
    da, db, dr = w
    return da + r * db + b * dr


def jets(z, demand, free, order=4):
    """Taylor coefficients, not derivatives, for constant input ODEs."""
    aa, bb, rr = ([Q(x)] for x in z)
    for n in range(order):
        aa.append((demand * (n == 0) - free * rr[n]) / (n + 1))
        bb.append((demand * rr[n] + free * (n == 0)) / (n + 1))
        rr.append(demand * bb[n] / (n + 1))
    return aa, bb, rr


def main():
    values = [Q(-1), Q(-1, 2), Q(0), Q(1, 2), Q(1)]
    count = 0
    for z in product(values, repeat=3):
        a, b, r = z
        tangent = (-r, Q(1), Q(0))
        assert drho(z, tangent) == 0
        for epsilon in values:
            assert rho((a-r*epsilon, b+epsilon, r)) == rho(z)
        for demand, free in product(values, repeat=2):
            w = velocity(z, demand, free)
            assert drho(z, w) == (1+r*r+b*b)*demand
            count += 1
        error = 1-rho(z)
        for free in values:
            denergy = -error * drho(z, velocity(z, error, free))
            assert denergy == -(1+r*r+b*b)*error*error
            assert denergy <= 0

    z0, z1 = (Q(0), Q(0), Q(0)), (Q(0), Q(0), Q(1))
    assert rho(z0) == rho(z1) == 0
    assert z0[:2] == z1[:2]
    assert velocity(z0, Q(1), Q(0)) == (1, 0, 0)
    assert velocity(z1, Q(1), Q(0)) == (1, 1, 0)
    left = jets(z0, Q(1), Q(0))
    right = jets(z1, Q(1), Q(0))
    assert left[1] == left[2] == [0]*5
    assert right[1] == [0, 1, 0, Q(1, 6), 0]
    assert right[2] == [1, 0, Q(1, 2), 0, Q(1, 24)]

    # Instantaneous output-neutral motion need not be neutral for later motion.
    # At r=0 both states below have rho=0; a pure v motion can connect them.
    z2 = (Q(0), Q(1), Q(0))
    assert rho(z0) == rho(z2)
    assert drho(z0, velocity(z0, Q(1), Q(0))) == 1
    assert drho(z2, velocity(z2, Q(1), Q(0))) == 2
    assert velocity(z0, Q(1), Q(0)) != velocity(z0, Q(1), Q(1))

    result = {
        'status': 'passed',
        'arithmetic': 'exact rational',
        'state_grid_count': len(values)**3,
        'state_input_combinations': count,
        'checks': [
            'tangent is output-neutral',
            'finite fixed-reference substitution preserves rho',
            'output derivative and positive gain identity',
            'ordinary error closure decreases squared error',
            'same current display and result; different response',
            'reference-response-reference loop in exact Taylor coefficients',
            'instantaneous neutrality does not imply future neutrality',
            'local free component is nontrivial'
        ],
        'right_reference_taylor_coefficients': [str(x) for x in right[2]],
        'not_verified': [
            'future demand source or reverse causality',
            'multiple complete paths satisfying fixed C',
            'reference return relation',
            'global difference identity',
            'minimality or equivalence of original theories'
        ]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
