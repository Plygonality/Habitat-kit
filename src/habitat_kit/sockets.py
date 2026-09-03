"""Shared actor and generator sockets.

Actors reuse Probe-kit's Scale / Attach / Hull / Glass contract, then add
Unit-canon length sockets. The generator is the one MODIFIER tree; it is
not a second actor catalog.
"""

from __future__ import annotations

from gn_as_code import Graph, SocketType
from gn_as_code.graph import SocketRef
from probe_kit.sockets import (
    ACTOR_KIND,
    add_actor_interface,
    new_actor_graph,
    place_actor,
)
from probe_kit.sockets import (
    ActorSockets as ProbeActorSockets,
)

from habitat_kit.canon import BLENDER, Measures, add_measures

GEOMETRY_SOCKET = "Geometry"

DECAY_SOCKETS: tuple[tuple[str, str, str], ...] = (
    ("Amount", "amount", "Time-slice decay-pass amount"),
    ("Incomplete", "incomplete", "Time-slice decay-pass incomplete"),
    ("Scaffold", "scaffold", "Time-slice decay-pass scaffold"),
    ("Oxidation", "oxidation", "Time-slice decay-pass oxidation"),
    ("Breach", "breach", "Time-slice decay-pass breach"),
    ("Debris", "debris", "Time-slice decay-pass debris"),
)

SIGNAL_SOCKETS: tuple[tuple[str, str, str], ...] = (
    ("Density", "density", "Time-slice signal-field density"),
    ("Coherence", "coherence", "Time-slice signal-field coherence"),
    ("Amplitude", "amplitude", "Time-slice signal-field amplitude"),
    ("Wavelength", "wavelength", "Time-slice signal-field wavelength"),
    ("Ghost", "ghost", "Time-slice signal-field ghost"),
)

EPOCH_SOCKET_NAMES: tuple[str, ...] = tuple(name for name, _, _ in DECAY_SOCKETS + SIGNAL_SOCKETS)


def add_epoch_inputs(g: Graph) -> dict[str, SocketRef]:
    """Decay-pass + signal-field as GN floats. Defaults stay at zero; states fill them."""
    refs: dict[str, SocketRef] = {}
    for name, _key, description in DECAY_SOCKETS + SIGNAL_SOCKETS:
        refs[name] = g.input_float(
            name,
            0.0,
            min=0.0,
            max=1.0,
            description=description,
        )
    return refs


def extra_attach(
    g: Graph,
    sockets: ProbeActorSockets,
    name: str,
    local: SocketRef,
) -> SocketRef:
    """Scale a local attach offset the same way Probe-kit does, without baking lengths."""
    slug = name.lower().replace(" ", "_")
    scaled = g.vector_math("SCALE", local, scale=sockets.scale, id=f"{slug}_scaled")
    g.output(scaled.vector, name=name, socket=SocketType.VECTOR)
    return scaled.vector


def start_actor(name: str) -> tuple[Graph, ProbeActorSockets, Measures]:
    g = new_actor_graph(name)
    sockets = add_actor_interface(g)
    measures = add_measures(g)
    return g, sockets, measures


def group_call_inputs(
    *,
    scale: SocketRef,
    location: SocketRef,
    rotation: SocketRef,
    hull: SocketRef,
    glass: SocketRef,
    measures: Measures,
) -> dict[str, SocketRef]:
    """Wire Probe-kit + Unit-canon sockets into a nested actor group."""
    return {
        "Scale": scale,
        "Attach Location": location,
        "Attach Rotation": rotation,
        "Hull": hull,
        "Glass": glass,
        "Meters Per Grid": measures.grid,
        "Deck Height": measures.deck,
        "Airlock Diameter": measures.airlock,
        "Human Standing Height": measures.figure,
        "Human Eye Height": measures.eye,
        "Human Shoulder Width": measures.shoulder,
    }


__all__ = [
    "ACTOR_KIND",
    "BLENDER",
    "DECAY_SOCKETS",
    "EPOCH_SOCKET_NAMES",
    "GEOMETRY_SOCKET",
    "SIGNAL_SOCKETS",
    "add_epoch_inputs",
    "extra_attach",
    "group_call_inputs",
    "new_actor_graph",
    "place_actor",
    "start_actor",
]
