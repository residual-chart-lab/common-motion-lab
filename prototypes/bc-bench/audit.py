"""Adversarial checks: B1 preserves a result but does not source motion from it."""
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
import numpy as np
from model import Params, result, rhs, rk4, simulate


def to_result_coordinates(z):
    a,b,p,r=z
    return np.array([a+r*b,b,p,r])


def transformed_velocity(z):
    a,b,p,r=z
    da,db,dp,dr=rhs(z)
    return np.array([da+r*db+b*dr,db,dp,dr])


def run():
    # All tangent velocities are (-r*u-b*w,u,v,w).
    # The last three components recover the three parameters uniquely.
    exact_cases=0
    for b,r,u,v,w in product(map(Q,[-1,0,1]),repeat=5):
        vel=(-r*u-b*w,u,v,w)
        assert vel[0]+r*vel[1]+b*vel[3]==0
        assert vel[1:]==(u,v,w)
        exact_cases+=1

    # Same forward-carried b,p,r; only the conserved result coordinate differs.
    trajectories={}
    for c in (-2.,0.,1.,3.):
        t,z=simulate(initial=[c,0.,1.,0.],duration=20.)
        trajectories[c]=z
        assert np.max(np.abs(result(z)-c))<1e-7
    base=trajectories[1.]
    carried_difference=max(float(np.max(np.abs(z[:,1:]-base[:,1:]))) for z in trajectories.values())
    offset_error=max(float(np.max(np.abs((z[:,0]-base[:,0])-(c-1)))) for c,z in trajectories.items())
    assert carried_difference==0.
    assert offset_error<1e-12

    rng=np.random.default_rng(20261001)
    conjugacy_error=0.
    for _ in range(100):
        z=rng.normal(size=4)
        expected=rhs(z)[1:]
        for c in (-2.,0.,1.,3.):
            zz=z.copy();zz[0]=c-zz[3]*zz[1]
            got=transformed_velocity(zz)
            conjugacy_error=max(conjugacy_error,float(np.max(np.abs(got-np.r_[0.,expected]))))
    assert conjugacy_error<1e-12

    # Smooth full-state flow is recoverable backward: monotone r is not proof
    # of mathematical noninvertibility. Negative dt is a diagnostic only.
    start=np.array([1.,0.,1.,0.]);z=start.copy()
    dt=.005;steps=2000
    for _ in range(steps):z=rk4(z,dt,Params())
    reference_increase=float(z[3]-start[3])
    for _ in range(steps):z=rk4(z,-dt,Params())
    recovery_error=float(np.max(np.abs(z-start)))
    assert reference_increase>0
    assert recovery_error<1e-8

    report={
        'status':'passed',
        'scientific_verdict':'B1 has no active result-to-motion connection; this is a negative audit finding',
        'tangent_parameter_checks':exact_cases,
        'arbitrary_tangent_functions':3,
        'tested_result_levels':[-2,0,1,3],
        'max_carried_state_difference_across_result_levels':carried_difference,
        'max_a_offset_error':offset_error,
        'max_coordinate_conjugacy_error':conjugacy_error,
        'forward_reference_increase':reference_increase,
        'forward_then_backward_full_state_error':recovery_error,
        'scope':'the exact B1 equations only; not a no-go theorem for future causality',
    }
    out=Path(__file__).parent/'results'/'source-audit.json'
    out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':run()
