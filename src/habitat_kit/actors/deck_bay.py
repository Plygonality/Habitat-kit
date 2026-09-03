"""Deck bay shell. Span and storey from Unit-canon deck height."""

from __future__ import annotations

from gn_as_code import Graph

from habitat_kit.primitives import box, join
from habitat_kit.sockets import extra_attach, place_actor, start_actor

GROUP_NAME = "HK Deck Bay"
GROUP_ID = "deck_bay"


def build_deck_bay() -> Graph:
    g, sockets, m = start_actor(GROUP_NAME)

    floor_size = g.combine_xyz(m.deck, m.deck, m.wall, id="floor_size").vector
    floor_loc = g.combine_xyz(m.zero, m.zero, m.half_wall, id="floor_loc").vector
    floor = box(g, floor_size, floor_loc, id="floor")

    ceil_z = g.math("SUBTRACT", m.deck, m.half_wall, id="ceil_z").value
    ceil_loc = g.combine_xyz(m.zero, m.zero, ceil_z, id="ceil_loc").vector
    ceiling = box(g, floor_size, ceil_loc, id="ceiling")

    wall_y_size = g.combine_xyz(m.deck, m.wall, m.deck, id="wall_y_size").vector
    wall_pos_y = box(
        g,
        wall_y_size,
        g.combine_xyz(m.zero, m.half_deck, m.half_deck, id="wall_pos_y_loc").vector,
        id="wall_pos_y",
    )
    wall_neg_y = box(
        g,
        wall_y_size,
        g.combine_xyz(m.zero, m.neg_half_deck, m.half_deck, id="wall_neg_y_loc").vector,
        id="wall_neg_y",
    )

    wall_x_size = g.combine_xyz(m.wall, m.deck, m.deck, id="wall_x_size").vector
    wall_pos_x = box(
        g,
        wall_x_size,
        g.combine_xyz(m.half_deck, m.zero, m.half_deck, id="wall_pos_x_loc").vector,
        id="wall_pos_x",
    )
    wall_neg_x = box(
        g,
        wall_x_size,
        g.combine_xyz(m.neg_half_deck, m.zero, m.half_deck, id="wall_neg_x_loc").vector,
        id="wall_neg_x",
    )

    hull = join(
        g,
        floor,
        ceiling,
        wall_pos_y,
        wall_neg_y,
        wall_pos_x,
        wall_neg_x,
        id="hull",
    )
    place_actor(g, sockets, hull)
    extra_attach(g, sockets, "Deck Attach", m.origin)
    return g
