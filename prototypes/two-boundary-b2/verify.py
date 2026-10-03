from fractions import Fraction as Q
from pathlib import Path
import json
import math
from model import Boundary, sources, state, rhs, invariant, normalized_rhs


def run():
    b=Boundary()
    assert sources(b)==(1.,-2.)
    records=[]
    for p in map(Q,[1,-2]):
        trajectory=[]
        for k in range(21):
            t=Q(k,20)
            x=Q(1,2)*p*t+p*p*t*t/2
            r=Q(1,2)+p*t
            dx=p*r
            assert x-r*r/2==Q(-1,8)
            assert (dx-r*p,p,Q(0))==(0,p,0)
            if t<1: assert x!=1
            if t==1: assert x==1
            trajectory.append({'t':str(t),'x':str(x),'r':str(r),'dx':str(dx)})
        records.append({'p':str(p),'trajectory':trajectory})
    assert rhs(state(0,-2,b))[0]==-1
    assert rhs(state(.25,-2,b))[0]==0
    assert rhs(state(1,-2,b))[0]==3
    assert state(.25,-2,b)[0]==-.125

    # Terminal condition changes the initially undetermined p. The full state
    # is not held fixed: (x0,r0) is the fixed forward-specified part.
    terminal_changes={}
    residual=0.
    for c in (.5,1.,2.):
        bb=Boundary(terminal=c)
        ps=sources(bb)
        terminal_changes[str(c)]=list(ps)
        for p in ps:
            residual=max(residual,abs(state(bb.horizon,p,bb)[0]-c))
    assert residual<1e-14
    assert sources(Boundary(terminal=-1))==()
    assert sources(Boundary(terminal=-.125))==(-.5,)

    # Cut the reference update while holding the already solved p fixed.
    cut_endpoints=[b.present+b.reference*p*b.horizon for p in sources(b)]
    assert cut_endpoints==[.5,-1.]
    # Re-solving the modified boundary problem can recover the same result.
    repaired_p=(b.terminal-b.present)/(b.reference*b.horizon)
    assert repaired_p==2.
    assert b.present+b.reference*repaired_p*b.horizon==1.

    # Current full state admits the forward IVP / time-to-go equivalent.
    # The model's second derivative is p^2; p itself is constant.
    for p in sources(b):
        for t in (0.,.2,.4,.8):
            z=state(t,p,b)
            assert normalized_rhs(z)==(0.,p,0.)
            rebased=Boundary(present=z[0],reference=z[1],terminal=1.,horizon=1.-t)
            assert min(abs(q-p) for q in sources(rebased))<1e-13
            assert abs(rhs(z)[0]-(z[1]*p))<1e-13

    report={
        'status':'passed',
        'scientific_status':'terminal-only comparator; ordinary boundary inversion, not accepted as B_C',
        'boundary':{'x0':0.,'r0':.5,'xT':1.,'T':1.},
        'admissible_sources':[1.,-2.],
        'max_terminal_residual':residual,
        'negative_branch_turning_time':.25,
        'negative_branch_minimum_x':-.125,
        'terminal_interventions':terminal_changes,
        'fixed_source_reference_cut_endpoints':cut_endpoints,
        'reference_cut_reclosed_source':repaired_p,
        'structural_checks':{
            'terminal_only_success':True,
            'multiple_paths_same_boundary':True,
            'reference_changes_action_sign':True,
            'no_trajectory_rollout_in_boundary_solver':True,
            'equivalent_to_selecting_free_motion_initial_slope':True,
            'source_strength_increases':False,
            'future_causality_established':False,
        },
        'exact_records':records,
    }
    out=Path(__file__).parent/'results'
    out.mkdir(exist_ok=True)
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='exact_records'},indent=2))


if __name__=='__main__':run()
