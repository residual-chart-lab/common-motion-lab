#!/usr/bin/env python3
"""Exact finite checks for Astra v1. Python standard library only.

Run from any directory; stdout is deterministic JSON. No sampling or floats.
The mathematical lower-bound proofs are in model.md, not inferred from a scan.
"""
import json
from itertools import product


def obs(z):
    return int(z == 1)


def step(z, a, n=3):
    return (z + a) % n


def trajectory(z, word, n=3):
    result = [z]
    for a in word:
        z = step(z, a, n)
        result.append(z)
    return result


def first_return(z, n=3):
    for t in range(1, n + 1):
        end = (z + t) % n
        if obs(end) == 0:
            return t, end
    raise AssertionError("No return")


def allowed(z, remaining, n=3):
    if remaining == 0:
        return []
    return [a for a in (-1, 1)
            if any(obs(trajectory(z, (a,) + tail, n)[-1]) == 0
                   for tail in product((-1, 1), repeat=remaining - 1))]


def response_partition(n, depth, actions=(-1, 1)):
    words = [w for k in range(depth + 1) for w in product(actions, repeat=k)]
    signatures = {}
    for z in range(n):
        signature = tuple(obs(trajectory(z, w, n)[-1]) for w in words)
        signatures.setdefault(signature, []).append(z)
    return list(signatures.values())


def periodic_boundary_property(mapping, outputs, start):
    """Infinite E checked exactly by exhausting the (state, time parity) orbit.

    Every even sample has the initial output and differs in state two steps
    later; at least one visited state has another output. Deterministic maps
    may have transients; the product-state repetition proves completeness.
    """
    seen = set()
    z, parity = start, 0
    varied = False
    while (z, parity) not in seen:
        seen.add((z, parity))
        varied |= outputs[z] != outputs[start]
        if parity == 0:
            if outputs[z] != outputs[start] or mapping[mapping[z]] == z:
                return False
        z, parity = mapping[z], 1 - parity
    return varied


def verify():
    report = {"arithmetic": "exact integers; exhaustive finite enumeration"}
    assert obs(0) == obs(2) and 0 != 2
    assert obs(step(0, 1)) != obs(step(2, 1))
    assert trajectory(0, (1, 1)) == [0, 1, 2]
    assert obs(2) == obs(0) and obs(step(2, 1)) != obs(step(0, 1))
    routes = []
    for word in product((-1, 1), repeat=2):
        path = trajectory(0, word)
        routes.append({"actions": list(word), "states": path,
                       "outputs": list(map(obs, path)), "allowed": obs(path[-1]) == 0})
    assert sum(r["allowed"] for r in routes) == 3
    assert len({tuple(r["states"]) for r in routes if r["allowed"]}) == 3
    report["A_D"] = {"passed": True, "two_step_routes": routes}
    returns = {str(z): list(first_return(z)) for z in (0, 2)}
    assert returns == {"0": [2, 2], "2": [1, 0]}
    report["first_returns"] = returns

    pair_checks = 0
    recurrence_checks = 0
    reconstruction_checks = 0
    # All one-step pair dynamics; induction extends preservation to any word.
    for z, other, a in product(range(3), range(3), (-1, 1)):
        assert (step(other, a) - step(z, a)) % 3 == (other - z) % 3
        pair_checks += 1
    # All local transitions are enough to check the recurrence for all runs.
    for z0, previous_action, action in product(range(3), (-1, 1), (-1, 1)):
        z1 = step(z0, previous_action)
        z2 = step(z1, action)
        prev, current, actual = map(obs, (z0, z1, z2))
        predicted = 1 - current - prev if action == previous_action else prev
        assert predicted == actual
        recurrence_checks += 1
        recovered = (1 + previous_action * (1 - current) * (2 * prev - 1)) % 3
        assert recovered == z1
        reconstruction_checks += 1
    report["difference_and_memory"] = {
        "one_step_pair_cases": pair_checks,
        "controlled_recurrence_cases": recurrence_checks,
        "state_reconstruction_cases": reconstruction_checks,
        "scope": "all local cases; identities compose to arbitrary finite trajectories"}

    report["response_classes"] = {"3_states_depth_0": response_partition(3, 0),
                                  "3_states_depth_1": response_partition(3, 1),
                                  "4_states_depth_1": response_partition(4, 1)}
    assert len(response_partition(3, 0)) == 2
    assert len(response_partition(3, 1)) == 3
    assert len(response_partition(4, 1)) == 4
    report["boundary_admissibility"] = {
        "start_0_two_steps_left": allowed(0, 2),
        "state_0_one_step_left": allowed(0, 1),
        "state_1_one_step_left": allowed(1, 1),
        "state_2_one_step_left": allowed(2, 1)}
    assert allowed(0, 2) == [-1, 1]
    assert allowed(0, 1) == [-1] and allowed(2, 1) == [1]
    assert allowed(1, 1) == [-1, 1]

    small_counts = {}
    for n in (1, 2, 3):
        checked, found = 0, []
        for mapping in product(range(n), repeat=n):
            for outputs in product((0, 1), repeat=n):
                for start in range(n):
                    checked += 1
                    if periodic_boundary_property(mapping, outputs, start):
                        found.append((mapping, outputs, start))
        assert not found
        small_counts[str(n)] = {"map_output_start_cases": checked, "E_witnesses": 0}
    map4 = tuple((z + 1) % 4 for z in range(4))
    assert periodic_boundary_property(map4, tuple(map(obs, range(4))), 0)
    assert obs(step(0, 1, 4)) != obs(step(2, 1, 4))
    extension_paths = [trajectory(0, w, 4) for w in product((-1, 1), repeat=3)]
    assert sum(obs(p[-1]) == 0 for p in extension_paths) == 4
    report["uniform_return_extension"] = {
        "smaller_models": small_counts,
        "4_state_positive_orbit": trajectory(0, (1,) * 8, 4),
        "outputs": list(map(obs, trajectory(0, (1,) * 8, 4))),
        "three_step_constraint": {"accepted": 4, "rejected": 4}}

    # A second four-state system witnesses exact observable period 2,
    # but its hidden difference is inaccessible under R alone.
    states = list(product((0, 1), repeat=2))
    def rotate(z):
        x, h = z
        return (x ^ 1, h ^ x)
    def probe(z):
        return z[1], z[0]
    for z in states:
        returned = rotate(rotate(z))
        assert returned == (z[0], z[1] ^ 1)
        assert probe(z)[0] != probe(returned)[0]
        # Pair orbit, not a finite cut-off, verifies no future R distinction.
        pair, seen = (z, returned), set()
        while pair not in seen:
            seen.add(pair)
            assert pair[0][0] == pair[1][0]
            pair = (rotate(pair[0]), rotate(pair[1]))
    report["exact_waveform_period_counterexample"] = {"initial_states": 4,
        "R_only_hidden_difference": "never detected; complete pair orbit checked",
        "additional_probe": "detected in one step"}
    report["status"] = "PASS"
    return report


if __name__ == "__main__":
    print(json.dumps(verify(), ensure_ascii=False, indent=2))
