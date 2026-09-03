from __future__ import annotations

import json
from pathlib import Path

from gn_as_code.dump import dumps

from habitat_kit.cli import _canonical_json, dump_texts
from habitat_kit.registry import ACTORS, GENERATOR, registry_dict

ROOT = Path(__file__).resolve().parents[1]
GRAPHS = ROOT / "graphs"


def test_dumped_graphs_match_builders() -> None:
    missing: list[str] = []
    drifted: list[str] = []
    expected = dump_texts(GRAPHS)
    for name, text in expected.items():
        path = GRAPHS / name
        if not path.exists():
            missing.append(name)
            continue
        if path.read_text(encoding="utf-8") != text:
            drifted.append(name)
    assert not missing, f"Missing dumps for {missing}. Run: python -m habitat_kit dump"
    assert not drifted, f"Dumps drifted for {drifted}. Run: python -m habitat_kit dump"


def test_dumped_json_is_gn_as_code() -> None:
    for spec in ACTORS:
        payload = json.loads((GRAPHS / f"{spec.id}.json").read_text(encoding="utf-8"))
        assert payload["format"] == "gn-as-code"
        assert payload["kind"] == "GROUP"
        assert payload["name"] == spec.name
        assert dumps(spec.graph().to_data()) == (GRAPHS / f"{spec.id}.json").read_text(
            encoding="utf-8"
        )
    payload = json.loads((GRAPHS / f"{GENERATOR.id}.json").read_text(encoding="utf-8"))
    assert payload["format"] == "gn-as-code"
    assert payload["kind"] == "MODIFIER"
    assert payload["name"] == GENERATOR.name


def test_registry_dump_matches() -> None:
    path = GRAPHS / "registry.json"
    assert path.read_text(encoding="utf-8") == _canonical_json(registry_dict())
