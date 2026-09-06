from __future__ import annotations

from gn_as_code.validate import validate

from habitat_kit.generator import GENERATOR_ID, build_habitat_module
from habitat_kit.registry import ACTORS, GENERATOR


def test_generator_id_is_stable() -> None:
    assert GENERATOR_ID == GENERATOR.id
    assert build_habitat_module().name == GENERATOR.name


def test_generator_validates() -> None:
    errors = validate(build_habitat_module().to_data())
    assert errors == []


def test_generator_kind_is_modifier_actors_are_groups() -> None:
    assert GENERATOR.graph().kind.value == "MODIFIER"
    for spec in ACTORS:
        assert spec.graph().kind.value == "GROUP"
