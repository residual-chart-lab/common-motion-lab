"""Checks the boundary contract and a deliberately non-retrocausal fixture."""
from fractions import Fraction as Q
from pathlib import Path
import json
import numpy as np
from model import Params, result, rhs, simulate, phase_state


def main():
    # Exact algebra: the result condition does not identify its transport.
    fixed_delta=(Q(0),Q(1))
    normals=[(Q(1),Q(0)),(Q(1),Q(1))]
    effects=[sum(x*y for x,y in zip(n,fixed_delta)) for n in normals]
    assert effects == [0,1]
    for r in (Q(-2),Q(0),Q(1),Q(3,2)):
        # Every q(t)=(1-r*u*t,u*t) maps to the same result set y1=1.
        for u in (Q(-2),Q(0),Q(1),Q(3)):
            for t in (Q(0),Q(1,2),Q(5)):
                a,b=1-r*u*t,u*t
                assert a+r*b==1
        # Same F=1 level set under affine scaling or cubic re-expression.
        for f in (Q(-3),Q(0),Q(1),Q(2),Q(5,2)):
            assert (f==1) == (1+7*(f-1)==1) == (1+(f-1)**3==1)

    rng=np.random.default_rng(20261001)
    max_constraint_derivative=0.
    for z in rng.normal(size=(200,4)):
        da,db,dp,dr=rhs(z)
        a,b,p,r=z
        derivative=da+r*db+b*dr
        max_constraint_derivative=max(max_constraint_derivative,abs(derivative))
        assert abs(derivative)<1e-12
        assert abs(b*db+p*dp)<1e-12

    variants={
        'moving_reference': (Params(), [1,0,1,0]),
        'reference_transport_off': (Params(transport=0), [1,0,1,0]),
        'reference_feedback_off': (Params(feedback=0), [1,0,1,0]),
        'stationary_same_result': (Params(), [1,0,0,0]),
        'opposite_initial_phase': (Params(), [1,0,-1,0]),
    }
    runs={}; results={}
    for name,(param,z0) in variants.items():
        t,z=simulate(param,initial=z0)
        residual=float(np.max(np.abs(result(z)-1)))
        assert residual<1e-7
        phase=np.unwrap(np.arctan2(z[:,1],z[:,2]))
        runs[name]=(t,z)
        results[name]={
            'max_result_residual':residual,
            'final_reference':float(z[-1,3]),
            'turns':float((phase[-1]-phase[0])/(2*np.pi)),
            'initial_velocity':rhs(z[0],param).tolist(),
            'final_state':z[-1].tolist(),
        }
    assert np.max(np.abs(runs['stationary_same_result'][1]-[1,0,0,0]))==0
    assert runs['moving_reference'][1][-1,3]>1
    assert np.max(np.abs(runs['reference_transport_off'][1][:,3]))==0
    # Matched moving states: squared-error gradient is zero, fixture is not.
    z=phase_state(.7)
    assert abs(result(z)-1)<1e-14
    assert np.linalg.norm(rhs(z))>.5
    gradient=np.array([1,z[3],0,z[1]])
    assert np.linalg.norm((1-result(z))*gradient)<1e-12

    # Exact one-turn readout return, distinct reference and next response.
    z0=phase_state(0.)
    z1=phase_state(2*np.pi)
    assert np.max(np.abs(z0[:3]-z1[:3]))<1e-14
    assert abs(z1[3]-z0[3]-.15*np.pi)<1e-14
    assert abs(rhs(z1)[0]-rhs(z0)[0])>.5

    endpoints={}
    for dt in (.02,.01,.005):
        _,z=simulate(dt=dt)
        endpoints[dt]=z[-1]
    coarse=float(np.max(np.abs(endpoints[.02]-endpoints[.01])))
    fine=float(np.max(np.abs(endpoints[.01]-endpoints[.005])))
    assert fine<1e-6 and fine<coarse/8

    report={
        'status':'passed',
        'result_condition':'F=a+r*b=1, imposed throughout the witness trajectory',
        'same_delta_future_result_effects':effects,
        'gauge_example_derivatives_at_result':[1,7,0],
        'constraint_derivative_max_error':float(max_constraint_derivative),
        'one_turn_reference_increment':float(z1[3]-z0[3]),
        'one_turn_readout_max_difference':float(np.max(np.abs(z0[:3]-z1[:3]))),
        'initial_a_velocity':float(rhs(z0)[0]),
        'a_velocity_after_one_turn':float(rhs(z1)[0]),
        'refinement_errors':[coarse,fine],
        'runs':results,
        'verdict':'comparison fixture passes its algebraic and numerical checks; B_C remains unconstructed',
        'not_established':['future boundary causes current motion','a unique connection follows from F=1',
                           'the displayed return is the intended general reference return',
                           'irreversibility','learning or consciousness'],
    }
    # Convert exact rationals to integers for a portable report.
    report['same_delta_future_result_effects']=[int(v) for v in effects]
    out=Path(__file__).parent/'results'
    out.mkdir(exist_ok=True)
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez_compressed(out/'traces.npz',time=runs['moving_reference'][0],
                        **{name:z for name,(_,z) in runs.items()})
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
