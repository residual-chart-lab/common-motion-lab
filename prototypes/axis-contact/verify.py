"""Intervention, equation equivalence, and numerical convergence checks."""
from dataclasses import replace
import json
from pathlib import Path
import numpy as np
from model import Params, VARIANTS, initial_state, rhs_scalar, rhs_network, simulate, metrics


def run():
    rng = np.random.default_rng(20260929)
    circuit_error = 0.0
    for _ in range(120):
        state = rng.normal(size=(3, 5))
        for p in VARIANTS.values():
            err = np.max(np.abs(rhs_scalar(state, p)-rhs_network(state, p)))
            circuit_error = max(circuit_error, float(err))
    assert circuit_error < 1e-12

    traces, result = {}, {}
    for name, p in VARIANTS.items():
        t, z = simulate(p)
        traces[name] = (t, z)
        result[name] = metrics(t, z)
        assert np.isfinite(z).all()
        assert result[name]['max_unit_circle_error'] < 2e-6
    normal = traces['coupled'][1]
    for name in ('axis_off', 'reference_frozen'):
        assert np.max(np.abs(traces[name][1][:, :, 4])) == 0
        assert max(abs(x) for x in result[name]['turns_per_node'][1:]) == 0
        assert result[name]['turns_per_node'][0] > 5
    assert np.min(normal[-1, :, 4]) > 0.1
    assert result['coupled']['turns_per_node'][2] > 1
    assert max(abs(x) for x in result['readout_only']['turns_per_node'][1:]) == 0
    assert result['readout_only']['scale_per_node'][0] > 1
    assert max(result['axis_reversed']['log_scale_per_node']) < 0
    exact_states = traces['exact_transport'][1]
    predicted_s = 0.5*Params().transport*np.log(
        (Params().regularizer+np.sum(exact_states[:, :, 2:4]**2, axis=2)) /
        (Params().regularizer+1)
    )
    assert np.max(np.abs(exact_states[:, :, 4]-predicted_s)) < 1e-7
    assert max(abs(x) for x in result['exact_transport']['log_scale_per_node']) < 0.1

    # Same present q,s, but a different reference: compare future response.
    a, b = initial_state(), initial_state(hidden_delta=0.1)
    assert np.array_equal(a[:, [0, 1, 4]], b[:, [0, 1, 4]])
    assert not np.allclose(rhs_network(a), rhs_network(b))
    _, hidden = simulate(hidden_delta=0.1)
    hidden_gap = float(np.linalg.norm(normal[-1]-hidden[-1]))
    assert hidden_gap > 1e-5

    # Time is not supplied to the autonomous vector field. Identical current
    # states always give identical velocities; integrator refinement must agree.
    endpoints = {}
    for dt in (0.04, 0.02, 0.01):
        _, z = simulate(dt=dt, sample_every=round(0.2/dt))
        endpoints[dt] = z[-1]
    coarse = float(np.max(np.abs(endpoints[0.04]-endpoints[0.02])))
    fine = float(np.max(np.abs(endpoints[0.02]-endpoints[0.01])))
    assert fine < 1e-5 and fine < coarse/8

    # A held reference cannot transport scale even when it is nonzero.
    test_state = rng.normal(size=(3, 5))
    assert np.all(rhs_network(test_state, replace(Params(), freeze_reference=True))[:, 4] == 0)

    report = {
        'status': 'passed', 'seed': 20260929,
        'circuit_samples': 120*len(VARIANTS), 'max_scalar_circuit_error': circuit_error,
        'max_endpoint_error_dt04_dt02': coarse,
        'max_endpoint_error_dt02_dt01': fine,
        'refinement_ratio': coarse/fine,
        'hidden_reference_final_state_gap': hidden_gap,
        'variants': result,
        'not_established': [
            'future-to-present causality', 'a fixed result condition C has been realized',
            'fractal branching or fractal dimension', 'general reference-return relation',
            'learning efficiency or standard NN training', 'consciousness or time experience',
            'global minimality or equivalence to the four original theories',
        ],
    }
    path = Path(__file__).parent/'results'
    path.mkdir(exist_ok=True)
    (path/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    np.savez_compressed(path/'trajectories.npz', time=traces['coupled'][0],
                        **{name: z for name, (_, z) in traces.items()}, hidden_reference=hidden)
    print(json.dumps({k: v for k, v in report.items() if k != 'variants'}, indent=2))
    for name, vals in result.items():
        print(name, 'turns=', np.round(vals['turns_per_node'], 3),
              'scale=', np.round(vals['scale_per_node'], 3))


if __name__ == '__main__':
    run()
