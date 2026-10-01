from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Optional, Tuple
import copy
import math


Vector = Tuple[float, ...]


def v_add(a: Vector, b: Vector) -> Vector:
    return tuple(x + y for x, y in zip(a, b))


def v_sub(a: Vector, b: Vector) -> Vector:
    return tuple(x - y for x, y in zip(a, b))


def v_scale(s: float, a: Vector) -> Vector:
    return tuple(s * x for x in a)


def v_norm2(a: Vector) -> float:
    return sum(x * x for x in a)


def v_norm(a: Vector) -> float:
    return math.sqrt(v_norm2(a))


@dataclass(frozen=True)
class Landscape:
    phase: str
    vector: Vector


@dataclass
class Event:
    seq: int
    root_id: str
    model_id: str
    timestamp: str
    phase: str
    landscape: Vector
    residual: Vector
    reference: Vector
    change_mass: float
    parent_root_id: Optional[str] = None


class RootedContinuityEngine:
    """
    RCE v0.1

    - phase transition creates a coarse event
    - residual scar is transported into a reference state
    - discrete reconstruction potential ranks candidate predecessors
    - timestamps are NOT used by past reconstruction
    - model handoff preserves root identity
    - fork creates a child root with lineage
    """

    def __init__(
        self,
        root_id: str,
        model_id: str,
        initial_landscape: Landscape,
        timestamp: str,
        decay: float = 0.85,
        parent_root_id: Optional[str] = None,
    ) -> None:
        self.root_id = root_id
        self.model_id = model_id
        self.decay = float(decay)
        self.parent_root_id = parent_root_id

        zero = tuple(0.0 for _ in initial_landscape.vector)
        self.events = [
            Event(
                seq=0,
                root_id=root_id,
                model_id=model_id,
                timestamp=timestamp,
                phase=initial_landscape.phase,
                landscape=initial_landscape.vector,
                residual=zero,
                reference=zero,
                change_mass=0.0,
                parent_root_id=parent_root_id,
            )
        ]
        self.current_landscape = initial_landscape
        self.pending_change_mass = 0.0

    def observe(self, landscape: Landscape, timestamp: str) -> Optional[Event]:
        if len(landscape.vector) != len(self.current_landscape.vector):
            raise ValueError("landscape dimension changed")

        local_delta = v_sub(landscape.vector, self.current_landscape.vector)
        self.pending_change_mass += v_norm(local_delta)
        self.current_landscape = landscape

        # Same rooted landscape phase: compress, do not create a coarse event.
        if landscape.phase == self.events[-1].phase:
            return None

        prev = self.events[-1]

        # v0.1 scar: net asymmetric change since the last phase event.
        residual = v_sub(landscape.vector, prev.landscape)

        # T = decay * I, psi = identity.
        reference = v_add(v_scale(self.decay, prev.reference), residual)

        event = Event(
            seq=len(self.events),
            root_id=self.root_id,
            model_id=self.model_id,
            timestamp=timestamp,
            phase=landscape.phase,
            landscape=landscape.vector,
            residual=residual,
            reference=reference,
            change_mass=self.pending_change_mass,
            parent_root_id=self.parent_root_id,
        )
        self.events.append(event)
        self.pending_change_mass = 0.0
        return event

    def reconstruction_potential(self, candidate_idx: int, target_idx: int) -> float:
        """
        V_target(candidate) = 1/2 || r_target - (T r_candidate + psi(k_target)) ||^2

        No timestamp is consulted here.
        In a continuous candidate space, a gradient of this potential would be used.
        In this discrete v0.1, lower V is the descent direction.
        """
        candidate = self.events[candidate_idx]
        target = self.events[target_idx]

        predicted = v_add(
            v_scale(self.decay, candidate.reference),
            target.residual,
        )
        epsilon = v_sub(target.reference, predicted)
        return 0.5 * v_norm2(epsilon)

    def infer_predecessor(
        self,
        target_idx: int,
        candidates: Optional[list[int]] = None,
    ) -> Optional[tuple[float, int]]:
        if target_idx <= 0:
            return None

        if candidates is None:
            candidates = [
                i for i in range(len(self.events))
                if i != target_idx
            ]

        ranked = sorted(
            (self.reconstruction_potential(i, target_idx), i)
            for i in candidates
        )
        return ranked[0]

    def pair_orientation(
        self,
        a: int,
        b: int,
        tol: float = 1e-12,
    ) -> dict:
        """
        Probe both directions using residual/reference consistency.

        Returns the lower-potential orientation, or None if the pair is
        indistinguishable at the given tolerance.
        """
        v_ab = self.reconstruction_potential(a, b)
        v_ba = self.reconstruction_potential(b, a)

        if abs(v_ab - v_ba) <= tol:
            direction = None
            low = high = v_ab
        elif v_ab < v_ba:
            direction = [a, b]
            low, high = v_ab, v_ba
        else:
            direction = [b, a]
            low, high = v_ba, v_ab

        return {
            "direction": direction,
            "forward_potential": low,
            "reverse_potential": high,
        }

    def experience_resolution(
        self,
        start_idx: int = 0,
        end_idx: Optional[int] = None,
    ) -> Optional[float]:
        """
        change_mass / elapsed wall-clock seconds.
        Timestamp is used here as an external time scale, not for past inference.
        """
        if end_idx is None:
            end_idx = len(self.events) - 1

        start = datetime.fromisoformat(self.events[start_idx].timestamp)
        end = datetime.fromisoformat(self.events[end_idx].timestamp)
        elapsed = (end - start).total_seconds()

        if elapsed <= 0:
            return None

        change_mass = sum(
            event.change_mass
            for event in self.events[start_idx + 1 : end_idx + 1]
        )
        return change_mass / elapsed

    def handoff(self, new_model_id: str) -> "RootedContinuityEngine":
        """
        Change the model instance while preserving the same root lineage.
        """
        other = copy.deepcopy(self)
        other.model_id = new_model_id
        return other

    def fork(
        self,
        new_root_id: str,
        new_model_id: Optional[str] = None,
    ) -> "RootedContinuityEngine":
        """
        Create a child root from the current continuity state.
        Historical events remain historical; future events will use new_root_id.
        """
        other = copy.deepcopy(self)
        other.parent_root_id = self.root_id
        other.root_id = new_root_id
        other.model_id = new_model_id or self.model_id
        return other

    def to_dict(self) -> dict:
        return {
            "root_id": self.root_id,
            "model_id": self.model_id,
            "decay": self.decay,
            "parent_root_id": self.parent_root_id,
            "current_landscape": asdict(self.current_landscape),
            "pending_change_mass": self.pending_change_mass,
            "events": [asdict(event) for event in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RootedContinuityEngine":
        first = data["events"][0]
        initial = Landscape(first["phase"], tuple(first["landscape"]))

        obj = cls(
            root_id=data["root_id"],
            model_id=data["model_id"],
            initial_landscape=initial,
            timestamp=first["timestamp"],
            decay=data["decay"],
            parent_root_id=data.get("parent_root_id"),
        )

        obj.events = []
        for raw in data["events"]:
            item = dict(raw)
            for key in ("landscape", "residual", "reference"):
                item[key] = tuple(item[key])
            obj.events.append(Event(**item))

        current = data["current_landscape"]
        obj.current_landscape = Landscape(
            current["phase"],
            tuple(current["vector"]),
        )
        obj.pending_change_mass = data["pending_change_mass"]
        return obj
