"""Exact two-boundary comparator. Not an implementation of the protected B_C.

x_dot=p*r; r_dot=p; p_dot=0, with x(0), r(0), and x(T)=c specified.
The terminal requirement determines admissible p, without trajectory search.
The source is nevertheless ordinary boundary inversion, as audited explicitly.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Boundary:
    present: float = 0.0
    reference: float = 0.5
    terminal: float = 1.0
    horizon: float = 1.0

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.present,self.reference,self.terminal,self.horizon)):
            raise ValueError('finite boundary data required')
        if self.horizon <= 0:
            raise ValueError('positive horizon required')


def sources(boundary):
    """Both algebraic branches; no ranking or default branch selection."""
    b=boundary
    discriminant=b.reference**2+2*(b.terminal-b.present)
    if discriminant<0:
        return ()
    if discriminant==0:
        return (-b.reference/b.horizon,)
    root=math.sqrt(discriminant)
    return ((-b.reference+root)/b.horizon,(-b.reference-root)/b.horizon)


def state(t,p,boundary):
    b=boundary
    return (b.present+b.reference*p*t+0.5*p*p*t*t,
            b.reference+p*t,p)


def rhs(z):
    x,r,p=z
    return (p*r,p,0.)


def invariant(z):
    x,r,p=z
    return x-r*r/2


def normalized_coordinates(z):
    x,r,p=z
    return (invariant(z),r,p)


def normalized_rhs(z):
    dx,dr,dp=rhs(z)
    return (dx-z[1]*dr,dr,dp)
