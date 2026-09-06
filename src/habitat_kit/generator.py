"""The one Habitat-kit generator.

Instances Probe-kit-contract actors (airlock, deck bay, truss, hatch) into a
brutalist / industrial habitat module. Epoch sockets reuse Time-slice decay
and signal names. Lengths come only from Unit-canon.
"""

from __future__ import annotations

from gn_as_code import Graph, GraphKind, SocketType
from gn_as_code.graph import NodeHandle, SocketRef

from habitat_kit.actors.airlock import GROUP_NAME as AIRLOCK_NAME
from habitat_kit.actors.deck_bay import GROUP_NAME as DECK_BAY_NAME
from habitat_kit.actors.hatch import GROUP_NAME as HATCH_NAME
from habitat_kit.actors.truss import GROUP_NAME as TRUSS_NAME
from habitat_kit.canon import BLENDER, Measures, add_measures
from habitat_kit.groups import call_group
from habitat_kit.primitives import box, join
from habitat_kit.sockets import add_epoch_inputs, group_call_inputs

GENERATOR_ID = "habitat_module"
GENERATOR_NAME = "HK Habitat Module"


def build_habitat_module() -> Graph:
    g = Graph(GENERATOR_NAME, kind=GraphKind.MODIFIER, blender=BLENDER)
    measures = add_measures(g)
    epoch = add_epoch_inputs(g)
    hull = g.input(
        "Hull",
        SocketType.MATERIAL,
        description="Master-Node metal (MN Metal). Bind a category master, not a unique shader.",
    )
    glass = g.input(
        "Glass",
        SocketType.MATERIAL,
        description="Master-Node glass (MN Glass). Canopy / dome / viewport.",
    )
    empty = _empty(g, measures)

    bay = _place_bay(g, measures, hull, glass, epoch["Incomplete"])
    truss = _actor(
        g,
        TRUSS_NAME,
        id="truss_unit",
        measures=measures,
        hull=hull,
        glass=glass,
        location=measures.origin,
        rotation=measures.identity_rot,
        scale=measures.unity,
    )
    columns = _instance_columns(g, measures, truss)
    beams = _instance_beams(g, measures, truss)
    airlock = _place_airlock(g, measures, hull, glass)
    hatch = _place_hatch(g, measures, hull, glass, epoch, empty)
    scaffold = _instance_scaffold(g, measures, truss, epoch["Scaffold"], empty)
    figure = _scale_figure(g, measures, hull)

    module = join(
        g,
        bay,
        columns,
        beams,
        airlock,
        hatch,
        scaffold,
        figure,
        id="module",
    )
    realized = g.realize_instances(module, id="realize")
    g.output_geometry(realized.geometry)
    return g


def _actor(
    g: Graph,
    group_name: str,
    *,
    id: str,
    measures: Measures,
    hull: SocketRef,
    glass: SocketRef,
    location: SocketRef,
    rotation: SocketRef,
    scale: SocketRef,
) -> NodeHandle:
    return call_group(
        g,
        group_name,
        id=id,
        inputs=group_call_inputs(
            scale=scale,
            location=location,
            rotation=rotation,
            hull=hull,
            glass=glass,
            measures=measures,
        ),
    )


def _place_bay(
    g: Graph,
    m: Measures,
    hull: SocketRef,
    glass: SocketRef,
    incomplete: SocketRef,
) -> NodeHandle:
    unit = _actor(
        g,
        DECK_BAY_NAME,
        id="bay",
        measures=m,
        hull=hull,
        glass=glass,
        location=m.origin,
        rotation=m.identity_rot,
        scale=m.unity,
    )
    live = g.math("SUBTRACT", m.unity, incomplete, id="bay_live").value
    scale = g.combine_xyz(m.unity, m.unity, live, id="bay_scale").vector
    return g.transform(unit, scale=scale, id="bay_state")


def _points(g: Graph, mesh: NodeHandle, *, id: str, radius: SocketRef) -> NodeHandle:
    return g.node(
        "GeometryNodeMeshToPoints",
        id=id,
        inputs={"Mesh": mesh, "Radius": radius},
    )


def _instance_columns(g: Graph, m: Measures, truss: NodeHandle) -> NodeHandle:
    grid = g.mesh_grid(
        size_x=m.deck,
        size_y=m.deck,
        vertices_x=m.two_int,
        vertices_y=m.two_int,
        id="column_grid",
    )
    pts = _points(g, grid, id="column_points", radius=m.half_wall)
    lifted = g.transform(
        pts,
        translation=g.combine_xyz(m.zero, m.zero, m.half_deck, id="column_lift").vector,
        id="column_sites",
    )
    return g.instance_on_points(lifted, truss, id="columns")


def _instance_beams(g: Graph, m: Measures, truss: NodeHandle) -> NodeHandle:
    x_line = g.mesh_line(
        count=m.two_int,
        start_location=g.combine_xyz(m.zero, m.neg_half_deck, m.zero, id="xbeam_start").vector,
        offset=g.combine_xyz(m.zero, m.deck, m.zero, id="xbeam_off").vector,
        id="xbeam_line",
    )
    x_pts = _points(g, x_line, id="xbeam_pts", radius=m.half_wall)
    x_floor = g.instance_on_points(x_pts, truss, rotation=m.along_x, id="x_floor")
    x_ceil = g.transform(
        x_floor,
        translation=g.combine_xyz(m.zero, m.zero, m.deck, id="x_to_ceil").vector,
        id="x_ceil",
    )

    y_line = g.mesh_line(
        count=m.two_int,
        start_location=g.combine_xyz(m.neg_half_deck, m.zero, m.zero, id="ybeam_start").vector,
        offset=g.combine_xyz(m.deck, m.zero, m.zero, id="ybeam_off").vector,
        id="ybeam_line",
    )
    y_pts = _points(g, y_line, id="ybeam_pts", radius=m.half_wall)
    y_floor = g.instance_on_points(y_pts, truss, rotation=m.along_y, id="y_floor")
    y_ceil = g.transform(
        y_floor,
        translation=g.combine_xyz(m.zero, m.zero, m.deck, id="y_to_ceil").vector,
        id="y_ceil",
    )
    return join(g, x_floor, x_ceil, y_floor, y_ceil, id="beams")


def _place_airlock(g: Graph, m: Measures, hull: SocketRef, glass: SocketRef) -> NodeHandle:
    loc = g.combine_xyz(m.zero, m.half_deck, m.eye, id="airlock_loc").vector
    return _actor(
        g,
        AIRLOCK_NAME,
        id="airlock",
        measures=m,
        hull=hull,
        glass=glass,
        location=loc,
        rotation=m.identity_rot,
        scale=m.unity,
    )


def _place_hatch(
    g: Graph,
    m: Measures,
    hull: SocketRef,
    glass: SocketRef,
    epoch: dict[str, SocketRef],
    empty: NodeHandle,
) -> NodeHandle:
    loc = g.combine_xyz(m.zero, m.neg_half_deck, m.eye, id="hatch_loc").vector
    hatch = _actor(
        g,
        HATCH_NAME,
        id="hatch",
        measures=m,
        hull=hull,
        glass=glass,
        location=loc,
        rotation=m.face_neg_y,
        scale=m.unity,
    )
    half = g.math("DIVIDE", m.unity, m.two, id="half_threshold").value
    gone = g.compare("GREATER_THAN", epoch["Breach"], half, id="hatch_gone")
    intact = g.switch(gone.result, hatch, empty, id="hatch_intact")

    drop = g.math("MULTIPLY", epoch["Debris"], m.grid, id="hatch_drop").value
    neg_drop = g.math("SUBTRACT", m.zero, drop, id="neg_drop").value
    fallen = g.transform(
        hatch,
        translation=g.combine_xyz(m.zero, m.zero, neg_drop, id="fallen_off").vector,
        id="hatch_fallen",
    )
    show_fallen = g.compare("GREATER_THAN", epoch["Debris"], half, id="has_debris")
    debris = g.switch(show_fallen.result, empty, fallen, id="hatch_debris")
    return join(g, intact, debris, id="hatch_state")


def _instance_scaffold(
    g: Graph,
    m: Measures,
    truss: NodeHandle,
    scaffold: SocketRef,
    empty: NodeHandle,
) -> NodeHandle:
    ring = g.node(
        "GeometryNodeMeshCircle",
        id="scaffold_ring",
        inputs={"Vertices": m.four_int, "Radius": m.half_deck},
    )
    pts = _points(g, ring, id="scaffold_pts", radius=m.half_wall)
    lifted = g.transform(
        pts,
        translation=g.combine_xyz(m.zero, m.zero, m.half_deck, id="scaffold_lift").vector,
        id="scaffold_sites",
    )
    instanced = g.instance_on_points(lifted, truss, id="scaffold_posts")
    live = g.compare("GREATER_THAN", scaffold, m.zero, id="has_scaffold")
    return g.switch(live.result, empty, instanced, id="scaffold_gate")


def _scale_figure(g: Graph, m: Measures, hull: SocketRef) -> NodeHandle:
    size = g.combine_xyz(m.shoulder, m.shoulder, m.figure, id="figure_size").vector
    beside = g.math("ADD", m.half_deck, m.grid, id="figure_beside").value
    x = g.math("ADD", beside, m.half_shoulder, id="figure_x").value
    z = g.math("DIVIDE", m.figure, m.two, id="figure_z").value
    loc = g.combine_xyz(x, m.zero, z, id="figure_loc").vector
    body = box(g, size, loc, id="figure")
    return g.set_material(body, hull, id="figure_hull")


def _empty(g: Graph, m: Measures) -> NodeHandle:
    size = g.combine_xyz(m.zero, m.zero, m.zero, id="empty_size").vector
    return g.mesh_cube(size=size, id="empty")
