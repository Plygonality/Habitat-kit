"""Every length in a dump is a Unit-canon socket or a node fed by one."""

from __future__ import annotations

from gn_as_code.ir import GraphData

from habitat_kit.canon import ORIENT_HALF, ORIENT_QUARTER
from habitat_kit.registry import ACTORS, GENERATOR

LENGTH_SOCKETS = {
    "Size",
    "Size X",
    "Size Y",
    "Radius",
    "Radius Top",
    "Radius Bottom",
    "Depth",
    "Offset Scale",
}

ORIENTATION = {
    0,
    ORIENT_QUARTER,
    ORIENT_HALF,
    -ORIENT_QUARTER,
    -ORIENT_HALF,
}


def _graphs() -> list[tuple[str, GraphData]]:
    items = [(spec.id, spec.graph().to_data()) for spec in ACTORS]
    items.append((GENERATOR.id, GENERATOR.graph().to_data()))
    return items


def test_mesh_lengths_are_links_not_literals() -> None:
    failures: list[str] = []
    for ident, data in _graphs():
        for node in data.nodes:
            if not node.type.startswith("GeometryNodeMesh") and node.type not in {
                "GeometryNodeMeshToPoints",
                "GeometryNodeMeshLine",
                "GeometryNodeMeshGrid",
                "GeometryNodeMeshCircle",
            }:
                continue
            for key in LENGTH_SOCKETS:
                if key in node.inputs:
                    failures.append(f"{ident}:{node.id}.{key}={node.inputs[key]!r}")
            if "Translation" in node.inputs:
                failures.append(f"{ident}:{node.id}.Translation={node.inputs['Translation']!r}")
            if "Offset" in node.inputs:
                failures.append(f"{ident}:{node.id}.Offset={node.inputs['Offset']!r}")
            if "Count" in node.inputs:
                failures.append(f"{ident}:{node.id}.Count={node.inputs['Count']!r}")
            if "Vertices" in node.inputs:
                failures.append(f"{ident}:{node.id}.Vertices={node.inputs['Vertices']!r}")
            if "Vertices X" in node.inputs:
                failures.append(f"{ident}:{node.id}.Vertices X={node.inputs['Vertices X']!r}")
            if "Vertices Y" in node.inputs:
                failures.append(f"{ident}:{node.id}.Vertices Y={node.inputs['Vertices Y']!r}")
    assert failures == [], "length / count literals in graphs:\n" + "\n".join(failures)


def test_transform_translations_are_links() -> None:
    failures: list[str] = []
    for ident, data in _graphs():
        for node in data.nodes:
            if node.type != "GeometryNodeTransform":
                continue
            if "Translation" in node.inputs:
                value = node.inputs["Translation"]
                if value not in ([0, 0, 0], (0, 0, 0), [0.0, 0.0, 0.0]):
                    failures.append(f"{ident}:{node.id}.Translation={value!r}")
    assert failures == [], "baked translations:\n" + "\n".join(failures)


def test_rotation_literals_are_orientation_only() -> None:
    failures: list[str] = []
    for ident, data in _graphs():
        for node in data.nodes:
            rotation = node.inputs.get("Rotation")
            if not isinstance(rotation, list):
                continue
            for part in rotation:
                if part not in ORIENTATION:
                    failures.append(f"{ident}:{node.id}.Rotation={rotation!r}")
                    break
    assert failures == [], "non-orientation rotation literals:\n" + "\n".join(failures)


def test_combine_xyz_literals_are_orientation_or_empty() -> None:
    """X/Y/Z literals on Combine XYZ may only be quarter/half turns."""
    failures: list[str] = []
    for ident, data in _graphs():
        for node in data.nodes:
            if node.type != "ShaderNodeCombineXYZ":
                continue
            for key in ("X", "Y", "Z"):
                if key not in node.inputs:
                    continue
                value = node.inputs[key]
                if value not in ORIENTATION:
                    failures.append(f"{ident}:{node.id}.{key}={value!r}")
    assert failures == [], "length-like Combine XYZ literals:\n" + "\n".join(failures)
