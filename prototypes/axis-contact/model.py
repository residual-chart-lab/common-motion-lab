"""Autonomous axis/reference lift candidate; no claim of future causality.

Each node has (qx, qy, rx, ry, log_scale). Numerical time steps approximate
one fixed continuous law; they are not model events, epochs or resets.
"""
from dataclasses import dataclass, replace
import math
import numpy as np


@dataclass(frozen=True)
class Params:
    axis: float = 1.0
    reference_rate: float = 1.2
    transport: float = 0.08
    angular_rate: float = 1.0
    reference_feedback: float = 0.2
    scale_feedback: float = 0.25
    regularizer: float = 0.2
    recruitment_scale: float = 0.7
    freeze_reference: bool = False
    readout_only: bool = False
    exact_transport: bool = False


def initial_state(nodes=3, hidden_delta=0.0):
    if nodes < 1:
        raise ValueError('at least one node is required')
    state = np.zeros((nodes, 5), dtype=float)
    state[:, 0] = state[:, 2] = 1.0
    state[0, 3] += hidden_delta
    return state


def rhs_scalar(state, p=Params()):
    """Readable per-node reference implementation."""
    out = np.zeros_like(state)
    for k, (qx, qy, rx, ry, s) in enumerate(state):
        if k == 0:
            gate = 1.0
        elif p.readout_only:
            gate = 0.0
        else:
            parent_s = state[k-1, 4]
            gate = parent_s**2 / (p.recruitment_scale**2 + parent_s**2)
        cross = rx*qy-ry*qx
        omega = p.angular_rate + p.reference_feedback*cross
        if not p.readout_only:
            omega += p.scale_feedback*math.tanh(s)
        dqx, dqy = -gate*omega*qy, gate*omega*qx
        drx, dry = (0.0, 0.0) if p.freeze_reference else (
            gate*p.reference_rate*(qx-rx),
            gate*p.reference_rate*(qy-ry),
        )
        swept = rx*drx+ry*dry if p.exact_transport else rx*dry-ry*drx
        ds = p.transport*p.axis*swept/(p.regularizer+rx*rx+ry*ry)
        out[k] = dqx, dqy, drx, dry, ds
    return out


def rhs_network(state, p=Params()):
    """Batched recurrent arithmetic circuit, independent of rhs_scalar.

    Fixed linear mixing, product gates, positive divisive normalization,
    and tanh. This is an exact executable circuit, not a trained MLP.
    """
    q, r, s = state[:, :2], state[:, 2:4], state[:, 4]
    gate = np.ones(len(state))
    if len(state) > 1:
        gate[1:] = 0 if p.readout_only else (
            s[:-1]**2 / (p.recruitment_scale**2+s[:-1]**2)
        )
    cross = r[:, 0]*q[:, 1]-r[:, 1]*q[:, 0]
    omega = p.angular_rate+p.reference_feedback*cross
    if not p.readout_only:
        omega = omega+p.scale_feedback*np.tanh(s)
    rotation = np.array([[0., 1.], [-1., 0.]])
    dq = (q @ rotation)*(gate*omega)[:, None]
    dr = np.zeros_like(r) if p.freeze_reference else (
        (q-r)*(gate*p.reference_rate)[:, None]
    )
    swept = np.sum(r*dr, axis=1) if p.exact_transport else (r[:, 0]*dr[:, 1]-r[:, 1]*dr[:, 0])
    ds = p.transport*p.axis*swept / (
        p.regularizer+np.sum(r*r, axis=1)
    )
    return np.column_stack((dq, dr, ds))


def rk4(state, dt, p, rhs=rhs_network):
    k1 = rhs(state, p)
    k2 = rhs(state+0.5*dt*k1, p)
    k3 = rhs(state+0.5*dt*k2, p)
    k4 = rhs(state+dt*k3, p)
    return state+dt*(k1+2*k2+2*k3+k4)/6


def simulate(p=Params(), *, duration=50.0, dt=0.02, nodes=3,
             hidden_delta=0.0, sample_every=5):
    if dt <= 0 or duration < 0 or sample_every < 1:
        raise ValueError('invalid integration arguments')
    steps = round(duration/dt)
    if not math.isclose(steps*dt, duration, abs_tol=1e-10):
        raise ValueError('duration must be an integer multiple of dt')
    state = initial_state(nodes, hidden_delta)
    times, records = [0.0], [state.copy()]
    for i in range(steps):
        state = rk4(state, dt, p)
        if (i+1) % sample_every == 0 or i+1 == steps:
            times.append((i+1)*dt)
            records.append(state.copy())
    return np.array(times), np.array(records)


def metrics(times, states):
    phases = np.unwrap(np.arctan2(states[:, :, 1], states[:, :, 0]), axis=0)
    return {
        'duration': float(times[-1]),
        'turns_per_node': ((phases[-1]-phases[0])/(2*np.pi)).tolist(),
        'log_scale_per_node': states[-1, :, 4].tolist(),
        'scale_per_node': np.exp(states[-1, :, 4]).tolist(),
        'max_unit_circle_error': float(np.max(np.abs(np.sum(states[:, :, :2]**2, axis=2)-1))),
        'final_state': states[-1].tolist(),
    }


VARIANTS = {
    'coupled': Params(),
    'axis_off': replace(Params(), axis=0),
    'reference_frozen': replace(Params(), freeze_reference=True),
    'readout_only': replace(Params(), readout_only=True),
    'axis_reversed': replace(Params(), axis=-1),
    'exact_transport': replace(Params(), exact_transport=True),
}
