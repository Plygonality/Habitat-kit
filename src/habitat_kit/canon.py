"""Unit-canon sockets and derived measures.

Every length in a Habitat-kit graph is a Group Input from Unit-canon or a
math node fed by those inputs. Factors (unity, two) are derived from the
grid so graphs do not store 1.0 / 2.0 / 3.0 as mesh sizes.
"""

from __future__ import annotations

from dataclasses import dataclass

from gn_as_code import Graph
from gn_as_code.graph import SocketRef
from unit_canon.gn_as_code import socket_specs
from unit_canon.load import load
from unit_canon.model import Canon

# Quarter-turn / half-turn are orientations, not lengths.
ORIENT_QUARTER = 1.570796
ORIENT_HALF = 3.141593

BLENDER = "4.2"


@dataclass(frozen=True)
class Measures:
    """Canon sockets plus lengths derived from them inside the graph."""

    grid: SocketRef
    deck: SocketRef
    airlock: SocketRef
    figure: SocketRef
    eye: SocketRef
    shoulder: SocketRef
    unity: SocketRef
    zero: SocketRef
    two: SocketRef
    two_int: SocketRef
    four_int: SocketRef
    sixteen_int: SocketRef
    radius: SocketRef
    grids_per_deck: SocketRef
    overhead: SocketRef
    wall: SocketRef
    half_deck: SocketRef
    half_wall: SocketRef
    half_grid: SocketRef
    half_shoulder: SocketRef
    neg_half_deck: SocketRef
    neg_half_wall: SocketRef
    origin: SocketRef
    identity_rot: SocketRef
    along_x: SocketRef
    along_y: SocketRef
    face_neg_y: SocketRef


def canon() -> Canon:
    return load()


def add_canon_inputs(g: Graph) -> dict[str, SocketRef]:
    """Declare the Unit-canon Group Inputs. Names match ``socket_specs()``."""
    refs: dict[str, SocketRef] = {}
    for spec in socket_specs():
        refs[spec.key] = g.input_float(
            spec.name,
            spec.value,
            min=spec.min_value,
            subtype="DISTANCE",
            description=spec.description,
        )
    return refs


def add_measures(g: Graph) -> Measures:
    """Canon inputs + derived lengths. Call once per graph."""
    refs = add_canon_inputs(g)
    grid = refs["meters_per_grid"]
    deck = refs["deck_height"]
    airlock = refs["airlock_diameter"]
    figure = refs["human_figure.standing_height"]
    eye = refs["human_figure.eye_height"]
    shoulder = refs["human_figure.shoulder_width"]

    unity = g.math("DIVIDE", grid, grid, id="canon_unity").value
    zero = g.math("SUBTRACT", grid, grid, id="canon_zero").value
    two = g.math("ADD", unity, unity, id="canon_two").value
    two_int = g.float_to_int(two, id="canon_two_int").integer
    four = g.math("ADD", two, two, id="canon_four").value
    four_int = g.float_to_int(four, id="canon_four_int").integer
    sixteen = g.math("MULTIPLY", four, four, id="canon_sixteen").value
    sixteen_int = g.float_to_int(sixteen, id="canon_sixteen_int").integer

    radius = g.math("DIVIDE", airlock, two, id="canon_radius").value
    grids_per_deck = g.math("DIVIDE", deck, grid, id="canon_grids_per_deck").value
    overhead = g.math("SUBTRACT", deck, figure, id="canon_overhead").value
    g.math("SUBTRACT", deck, eye, id="canon_above_eye")
    wall = g.math("DIVIDE", shoulder, grids_per_deck, id="canon_wall").value
    half_deck = g.math("DIVIDE", deck, two, id="canon_half_deck").value
    half_wall = g.math("DIVIDE", wall, two, id="canon_half_wall").value
    half_grid = g.math("DIVIDE", grid, two, id="canon_half_grid").value
    half_shoulder = g.math("DIVIDE", shoulder, two, id="canon_half_shoulder").value
    neg_unity = g.math("SUBTRACT", zero, unity, id="canon_neg_unity").value
    neg_half_deck = g.math("MULTIPLY", half_deck, neg_unity, id="canon_neg_half_deck").value
    neg_half_wall = g.math("MULTIPLY", half_wall, neg_unity, id="canon_neg_half_wall").value

    origin = g.combine_xyz(zero, zero, zero, id="canon_origin").vector
    identity_rot = g.combine_xyz(zero, zero, zero, id="canon_identity_rot").vector
    along_x = g.combine_xyz(zero, ORIENT_QUARTER, zero, id="canon_along_x").vector
    along_y = g.combine_xyz(ORIENT_QUARTER, zero, zero, id="canon_along_y").vector
    face_neg_y = g.combine_xyz(zero, zero, ORIENT_HALF, id="canon_face_neg_y").vector

    return Measures(
        grid=grid,
        deck=deck,
        airlock=airlock,
        figure=figure,
        eye=eye,
        shoulder=shoulder,
        unity=unity,
        zero=zero,
        two=two,
        two_int=two_int,
        four_int=four_int,
        sixteen_int=sixteen_int,
        radius=radius,
        grids_per_deck=grids_per_deck,
        overhead=overhead,
        wall=wall,
        half_deck=half_deck,
        half_wall=half_wall,
        half_grid=half_grid,
        half_shoulder=half_shoulder,
        neg_half_deck=neg_half_deck,
        neg_half_wall=neg_half_wall,
        origin=origin,
        identity_rot=identity_rot,
        along_x=along_x,
        along_y=along_y,
        face_neg_y=face_neg_y,
    )
