"""Primitive helpers that take graph sockets, never length literals."""

from __future__ import annotations

from gn_as_code import Graph
from gn_as_code.graph import InputValue, NodeHandle

from habitat_kit.canon import Measures


def box(
    g: Graph,
    size: InputValue,
    location: InputValue,
    *,
    id: str,
    rotation: InputValue | None = None,
) -> NodeHandle:
    mesh = g.mesh_cube(size=size, id=f"{id}_mesh")
    if rotation is None:
        return g.transform(mesh, translation=location, id=id)
    return g.transform(mesh, translation=location, rotation=rotation, id=id)


def cylinder(
    g: Graph,
    *,
    radius: InputValue,
    depth: InputValue,
    measures: Measures,
    id: str,
    location: InputValue | None = None,
    rotation: InputValue | None = None,
) -> NodeHandle:
    mesh = g.mesh_cylinder(
        vertices=measures.sixteen_int,
        radius=radius,
        depth=depth,
        id=f"{id}_mesh",
    )
    translation = measures.origin if location is None else location
    if rotation is None:
        return g.transform(mesh, translation=translation, id=id)
    return g.transform(mesh, translation=translation, rotation=rotation, id=id)


def join(g: Graph, *parts: InputValue, id: str) -> NodeHandle:
    return g.join_geometry(*parts, id=id)
