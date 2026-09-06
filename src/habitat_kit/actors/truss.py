"""Truss member. Span is one deck; section is derived wall thickness."""

from __future__ import annotations

from gn_as_code import Graph

from habitat_kit.primitives import box, cylinder, join
from habitat_kit.sockets import extra_attach, place_actor, start_actor

GROUP_NAME = "HK Truss"
GROUP_ID = "truss"


def build_truss() -> Graph:
    g, sockets, m = start_actor(GROUP_NAME)

    shaft = cylinder(
        g,
        radius=m.half_wall,
        depth=m.deck,
        measures=m,
        id="shaft",
    )
    cap_size = g.combine_xyz(m.wall, m.wall, m.wall, id="cap_size").vector
    cap_a = box(
        g,
        cap_size,
        g.combine_xyz(m.zero, m.zero, m.half_deck, id="cap_a_loc").vector,
        id="cap_a",
    )
    cap_b = box(
        g,
        cap_size,
        g.combine_xyz(m.zero, m.zero, m.neg_half_deck, id="cap_b_loc").vector,
        id="cap_b",
    )
    hull = join(g, shaft, cap_a, cap_b, id="hull")
    place_actor(g, sockets, hull)
    end = g.combine_xyz(m.zero, m.zero, m.half_deck, id="end_local").vector
    extra_attach(g, sockets, "End Attach", end)
    return g
