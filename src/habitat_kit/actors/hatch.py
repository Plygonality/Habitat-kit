"""Circular hatch. Clear opening is the Unit-canon airlock diameter."""

from __future__ import annotations

from gn_as_code import Graph

from habitat_kit.primitives import cylinder
from habitat_kit.sockets import extra_attach, place_actor, start_actor

GROUP_NAME = "HK Hatch"
GROUP_ID = "hatch"


def build_hatch() -> Graph:
    g, sockets, m = start_actor(GROUP_NAME)

    ring = cylinder(
        g,
        radius=m.radius,
        depth=m.wall,
        measures=m,
        rotation=m.along_y,
        id="ring",
    )
    pane = cylinder(
        g,
        radius=m.half_shoulder,
        depth=m.half_wall,
        measures=m,
        rotation=m.along_y,
        id="pane",
    )
    place_actor(g, sockets, ring, pane)
    extra_attach(g, sockets, "Hatch Attach", m.origin)
    return g
