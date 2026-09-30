"""A result-preserving comparison fixture, not a future-causality mechanism.

The imposed condition F=a+r*b=1 holds for the entire trajectory. This is
stronger than a terminal condition alone and is not derived from that alone.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Params:
    transport: float = 0.15
    feedback: float = 0.3


def result(z):
    a, b, p, r = np.asarray(z).T
    return a+r*b


def rhs(z, params=Params()):
    a, b, p, r = z
    w = 1+params.feedback*np.tanh(r)
    db = w*p
    dp = -w*b
    dr = params.transport*w*p*p
    da = -r*db-b*dr
    return np.array([da, db, dp, dr])


def rk4(z, dt, p):
    a = rhs(z,p)
    b = rhs(z+dt*a/2,p)
    c = rhs(z+dt*b/2,p)
    d = rhs(z+dt*c,p)
    return z+dt*(a+2*b+2*c+d)/6


def simulate(params=Params(), *, duration=30., dt=.01, initial=None):
    n=round(duration/dt)
    if dt <= 0 or not np.isclose(n*dt,duration):
        raise ValueError('duration must be a nonnegative integer multiple of dt')
    z=np.array([1.,0.,1.,0.]) if initial is None else np.array(initial,dtype=float)
    trace=[z.copy()]
    for _ in range(n):
        z=rk4(z,dt,params)
        trace.append(z.copy())
    return np.linspace(0,duration,n+1),np.array(trace)


def phase_state(theta, *, radius=1., reference0=0., params=Params()):
    """Exact orbit for b(0)=0, p(0)=radius; physical timing remains nonuniform."""
    b=radius*np.sin(theta)
    p=radius*np.cos(theta)
    r=reference0+params.transport*radius**2*(theta/2+np.sin(2*theta)/4)
    a=1-r*b
    return np.array([a,b,p,r])
