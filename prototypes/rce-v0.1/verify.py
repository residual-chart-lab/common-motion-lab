from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

from rce import Landscape, RootedContinuityEngine


def build_demo() -> RootedContinuityEngine:
    t0 = datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)

    engine = RootedContinuityEngine(
        root_id="root-A",
        model_id="model-1",
        initial_landscape=Landscape("A", (0.0, 0.0, 0.0)),
        timestamp=t0.isoformat(),
    )

    observations = [
        (Landscape("A", (0.1, 0.0, 0.0)), 5),
        (Landscape("B", (1.0, 0.2, 0.0)), 10),
        (Landscape("B", (1.1, 0.25, 0.0)), 15),
        (Landscape("C", (1.2, 1.0, 0.1)), 30),
        (Landscape("D", (0.5, 1.2, 1.0)), 50),
    ]

    for landscape, minutes in observations:
        engine.observe(
            landscape,
            (t0 + timedelta(minutes=minutes)).isoformat(),
        )

    return engine


def main() -> None:
    engine = build_demo()

    predecessor_checks = []
    for target in range(1, len(engine.events)):
        potential, inferred = engine.infer_predecessor(target)
        predecessor_checks.append(
            {
                "target": target,
                "expected_predecessor": target - 1,
                "inferred_predecessor": inferred,
                "potential": potential,
            }
        )

    orientation_checks = []
    for i in range(len(engine.events) - 1):
        orientation_checks.append(
            {
                "pair": [i, i + 1],
                **engine.pair_orientation(i, i + 1),
            }
        )

    handoff = engine.handoff("model-2")
    child = engine.fork("root-B", "model-3")

    serialized = engine.to_dict()
    restored = RootedContinuityEngine.from_dict(
        json.loads(json.dumps(serialized))
    )

    report = {
        "status": "passed",
        "event_count": len(engine.events),
        "phases": [event.phase for event in engine.events],
        "predecessor_inference": predecessor_checks,
        "pair_orientation": orientation_checks,
        "handoff_root_same": handoff.root_id == engine.root_id,
        "fork_parent_ok": (
            child.parent_root_id == engine.root_id
            and child.root_id == "root-B"
        ),
        "serialization_roundtrip": restored.to_dict() == serialized,
        "experience_resolution_per_second": engine.experience_resolution(),
        "notes": [
            "past reconstruction does not consult timestamps",
            "phase labels are an external adapter in v0.1",
            "the prototype records residual scars during actual forward operation",
            "this is not a proof of spontaneous time orientation from an unordered world",
        ],
    }

    assert report["event_count"] == 4
    assert all(
        item["inferred_predecessor"] == item["expected_predecessor"]
        for item in predecessor_checks
    )
    assert all(
        item["direction"] == item["pair"]
        for item in orientation_checks
    )
    assert report["handoff_root_same"]
    assert report["fork_parent_ok"]
    assert report["serialization_roundtrip"]

    out = Path(__file__).parent / "results" / "verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
