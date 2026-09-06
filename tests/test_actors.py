from __future__ import annotations

from gn_as_code import GraphKind, SocketType, validate
from gn_as_code.types import jsonify
from probe_kit.sockets import SHARED_INPUTS, SHARED_OUTPUTS
from unit_canon.gn_as_code import defaults_by_socket_name, socket_specs

from habitat_kit.registry import ACTORS, GENERATOR, get_actor, registry_dict


def test_one_generator() -> None:
    assert GENERATOR.kind == GraphKind.MODIFIER
    assert GENERATOR.id == "habitat_module"
    assert GENERATOR.name == "HK Habitat Module"
    data = GENERATOR.graph().to_data()
    assert data.kind == GraphKind.MODIFIER
    assert validate(data) == []


def test_generator_instances_all_actors() -> None:
    data = GENERATOR.graph().to_data()
    labels = {node.label for node in data.nodes if node.type == "GeometryNodeGroup"}
    assert labels == {spec.name for spec in ACTORS}
    instance_nodes = [node for node in data.nodes if node.type == "GeometryNodeInstanceOnPoints"]
    assert instance_nodes, "generator must instance actors, not only place one copy"


def test_every_actor_is_a_valid_group() -> None:
    assert [spec.id for spec in ACTORS] == ["airlock", "deck_bay", "truss", "hatch"]
    for spec in ACTORS:
        data = spec.graph().to_data()
        assert data.kind == GraphKind.GROUP, spec.id
        assert validate(data) == [], (spec.id, [str(e) for e in validate(data)])


def test_shared_probe_kit_sockets() -> None:
    for spec in ACTORS:
        data = spec.graph().to_data()
        inputs = {item.name: item for item in data.interface_inputs}
        outputs = {item.name: item for item in data.interface_outputs}
        for name in SHARED_INPUTS:
            assert name in inputs, spec.id
        for name in SHARED_OUTPUTS:
            assert name in outputs, spec.id
        assert inputs["Scale"].socket == SocketType.FLOAT
        assert inputs["Hull"].socket == SocketType.MATERIAL
        assert inputs["Glass"].socket == SocketType.MATERIAL


def test_canon_sockets_on_every_graph() -> None:
    names = [spec.name for spec in socket_specs()]
    expected = defaults_by_socket_name()
    graphs = [(spec.id, spec.graph()) for spec in ACTORS]
    graphs.append((GENERATOR.id, GENERATOR.graph()))
    for ident, graph in graphs:
        data = graph.to_data()
        inputs = {item.name: item for item in data.interface_inputs}
        for name in names:
            assert name in inputs, (ident, name)
            assert inputs[name].socket == SocketType.FLOAT
            assert jsonify(inputs[name].default) == jsonify(expected[name])
            assert inputs[name].subtype == "DISTANCE"
        wired = {ln.from_socket for ln in data.links if ln.from_node == "Group Input"}
        for name in names:
            assert name in wired, f"{ident} never uses canon socket {name!r}"


def test_get_actor_accepts_id_or_group_name() -> None:
    by_id = get_actor("airlock")
    by_name = get_actor("HK Airlock")
    assert by_id is by_name
    try:
        get_actor("nope")
    except KeyError as err:
        assert "airlock" in str(err)
    else:
        raise AssertionError("expected KeyError")


def test_registry_dict_contract() -> None:
    payload = registry_dict()
    assert payload["format"] == "habitat-kit-registry"
    assert payload["generator"]["id"] == "habitat_module"
    assert payload["states"] == ["construction", "operational", "relic"]
    assert payload["epochs"] == "time_slice.EPOCHS"
    assert [g["id"] for g in payload["groups"]] == ["airlock", "deck_bay", "truss", "hatch"]
