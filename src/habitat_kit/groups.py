"""Nest a Probe-kit-style actor group inside the one generator."""

from __future__ import annotations

from gn_as_code import Graph
from gn_as_code.graph import InputValue, NodeHandle


def call_group(
    g: Graph,
    group_name: str,
    *,
    id: str,
    inputs: dict[str, InputValue],
) -> NodeHandle:
    """GeometryNodeGroup. ``label`` is the node-tree name the apply script binds."""
    return g.node(
        "GeometryNodeGroup",
        id=id,
        label=group_name,
        inputs=inputs,
        properties={"node_tree": group_name},
    )
