"""Airlock tube. Diameter and depth from Unit-canon."""

from __future__ import annotations

from gn_as_code import Graph

from habitat_kit.primitives import cylinder, join
from habitat_kit.sockets import extra_attach, place_actor, start_actor

GROUP_NAME = "HK Airlock"
GROUP_ID = "airlock"


def build_airlock() -> Graph:
    g, sockets, m = start_actor(GROUP_NAME)

    tube = cylinder(
        g,
        radius=m.radius,
        depth=m.grid,
        measures=m,
        rotation=m.along_y,
        id="tube",
    )
    flange_radius = g.math("ADD", m.radius, m.wall, id="flange_radius").value
    flange = cylinder(
        g,
        radius=flange_radius,
        depth=m.wall,
        measures=m,
        rotation=m.along_y,
        id="flange",
    )
    hull = join(g, tube, flange, id="hull")

    viewport = cylinder(
        g,
        radius=m.half_shoulder,
        depth=m.half_wall,
        measures=m,
        rotation=m.along_y,
        id="viewport",
    )

    place_actor(g, sockets, hull, viewport)
    dock = g.combine_xyz(m.zero, m.half_grid, m.zero, id="dock_local").vector
    extra_attach(g, sockets, "Dock Attach", dock)
    return g
