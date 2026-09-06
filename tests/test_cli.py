from __future__ import annotations

import json
from pathlib import Path

from habitat_kit.apply import to_apply_script
from habitat_kit.cli import main
from habitat_kit.registry import ACTORS, GENERATOR
from habitat_kit.states import EPOCHS


def test_cli_list_and_validate(capsys) -> None:
    assert main(["list"]) == 0
    listed = capsys.readouterr().out
    assert "habitat-kit-registry" in listed
    assert "habitat_module" in listed
    assert "airlock" in listed
    assert main(["validate"]) == 0
    validated = capsys.readouterr().out
    for spec in ACTORS:
        assert f"{spec.id}: ok" in validated
    assert f"{GENERATOR.id}: ok" in validated


def test_cli_states(capsys) -> None:
    assert main(["states"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert [item["id"] for item in payload] == list(EPOCHS)
    assert payload[0]["source"] == "time_slice.EPOCHS"


def test_cli_apply_script_mentions_generator(capsys) -> None:
    assert main(["apply-script", "--all-states"]) == 0
    script = capsys.readouterr().out
    assert "HK Habitat Module" in script
    assert "apply_habitat_graph" in script
    assert "construction" in script
    assert "operational" in script
    assert "relic" in script
    compile(script, "<habitat-apply>", "exec")


def test_apply_script_helper_compiles(tmp_path: Path) -> None:
    script = to_apply_script("relic", object_name="HabitatModule")
    compile(script, str(tmp_path / "apply.py"), "exec")
    assert "HK Airlock" in script
    assert "viewport.png" in script
