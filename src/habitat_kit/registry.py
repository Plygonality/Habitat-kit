"""Habitat-kit registry: four Probe-kit actors, one generator.

Scatter lives in the generator. Actors are the instances.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from gn_as_code import Graph, GraphKind
from probe_kit.materials import BINDINGS
from probe_kit.registry import ActorSpec, AttachSocket
from probe_kit.sockets import ACTOR_KIND, SHARED_INPUTS, SHARED_OUTPUTS
from unit_canon.gn_as_code import socket_specs

from habitat_kit.actors.airlock import GROUP_ID as AIRLOCK_ID
from habitat_kit.actors.airlock import GROUP_NAME as AIRLOCK_NAME
from habitat_kit.actors.airlock import build_airlock
from habitat_kit.actors.deck_bay import GROUP_ID as DECK_BAY_ID
from habitat_kit.actors.deck_bay import GROUP_NAME as DECK_BAY_NAME
from habitat_kit.actors.deck_bay import build_deck_bay
from habitat_kit.actors.hatch import GROUP_ID as HATCH_ID
from habitat_kit.actors.hatch import GROUP_NAME as HATCH_NAME
from habitat_kit.actors.hatch import build_hatch
from habitat_kit.actors.truss import GROUP_ID as TRUSS_ID
from habitat_kit.actors.truss import GROUP_NAME as TRUSS_NAME
from habitat_kit.actors.truss import build_truss
from habitat_kit.canon import BLENDER
from habitat_kit.generator import GENERATOR_ID, GENERATOR_NAME, build_habitat_module
from habitat_kit.sockets import EPOCH_SOCKET_NAMES
from habitat_kit.states import EPOCHS

FORMAT = "habitat-kit-registry"
FORMAT_VERSION = 1
INTERFACE_VERSION = 1
CONSTRAINT = (
    "Every length comes from Unit-canon "
    "(meters_per_grid 1.0, deck 3.0, airlock 1.0, figure 1.80); "
    "no magic numbers in graphs."
)

CANON_INPUTS = tuple(spec.name for spec in socket_specs())


AIRLOCK = ActorSpec(
    id=AIRLOCK_ID,
    name=AIRLOCK_NAME,
    label="Airlock",
    description="Circular airlock tube. Diameter and depth from Unit-canon.",
    build=build_airlock,
    attach=(
        AttachSocket(
            "Attach",
            role="dock",
            space="world",
            description="Tube center. Plant on a hull face.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "Dock Attach",
            role="dock_outer",
            space="local",
            description="Outer rim along +Y. Local offset, already scaled.",
        ),
    ),
    extra_inputs=CANON_INPUTS,
    extra_outputs=("Dock Attach",),
)

DECK_BAY = ActorSpec(
    id=DECK_BAY_ID,
    name=DECK_BAY_NAME,
    label="Deck bay",
    description="One-deck habitat bay. Span equals Unit-canon deck height.",
    build=build_deck_bay,
    attach=(
        AttachSocket(
            "Attach",
            role="floor",
            space="world",
            description="Floor center. Origin of the bay.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "Deck Attach",
            role="deck",
            space="local",
            description="Floor plane. Local origin, already scaled.",
        ),
    ),
    extra_inputs=CANON_INPUTS,
    extra_outputs=("Deck Attach",),
)

TRUSS = ActorSpec(
    id=TRUSS_ID,
    name=TRUSS_NAME,
    label="Truss",
    description="Structural member one deck long. Section from Unit-canon.",
    build=build_truss,
    attach=(
        AttachSocket(
            "Attach",
            role="centroid",
            space="world",
            description="Member centroid.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "End Attach",
            role="end",
            space="local",
            description="+Z end cap. Local offset, already scaled.",
        ),
    ),
    extra_inputs=CANON_INPUTS,
    extra_outputs=("End Attach",),
)

HATCH = ActorSpec(
    id=HATCH_ID,
    name=HATCH_NAME,
    label="Hatch",
    description="Circular hatch. Clear opening is the Unit-canon airlock diameter.",
    build=build_hatch,
    attach=(
        AttachSocket(
            "Attach",
            role="panel",
            space="world",
            description="Hatch center. Plant on a hull face.",
            local=(0.0, 0.0, 0.0),
        ),
        AttachSocket(
            "Hatch Attach",
            role="hatch",
            space="local",
            description="Panel center. Local origin, already scaled.",
        ),
    ),
    extra_inputs=CANON_INPUTS,
    extra_outputs=("Hatch Attach",),
)

ACTORS: tuple[ActorSpec, ...] = (AIRLOCK, DECK_BAY, TRUSS, HATCH)
ACTORS_BY_ID: dict[str, ActorSpec] = {spec.id: spec for spec in ACTORS}
ACTORS_BY_NAME: dict[str, ActorSpec] = {spec.name: spec for spec in ACTORS}


@dataclass(frozen=True)
class GeneratorSpec:
    id: str
    name: str
    label: str
    description: str
    build: Callable[[], Graph]
    kind: GraphKind = GraphKind.MODIFIER
    blender: str = BLENDER
    actors: tuple[str, ...] = tuple(spec.id for spec in ACTORS)

    def graph(self) -> Graph:
        return self.build()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "label": self.label,
            "description": self.description,
            "kind": self.kind.value,
            "blender": self.blender,
            "actors": list(self.actors),
            "canon_inputs": list(CANON_INPUTS),
            "epoch_inputs": list(EPOCH_SOCKET_NAMES),
            "states": list(EPOCHS),
        }


GENERATOR = GeneratorSpec(
    id=GENERATOR_ID,
    name=GENERATOR_NAME,
    label="Habitat module",
    description=(
        "One Geometry Nodes generator. Instances airlock, deck bay, truss, and hatch "
        "into a brutalist / industrial habitat module."
    ),
    build=build_habitat_module,
)


def list_actors() -> Sequence[ActorSpec]:
    return ACTORS


def get_actor(id_or_name: str) -> ActorSpec:
    if id_or_name in ACTORS_BY_ID:
        return ACTORS_BY_ID[id_or_name]
    if id_or_name in ACTORS_BY_NAME:
        return ACTORS_BY_NAME[id_or_name]
    known = ", ".join(spec.id for spec in ACTORS)
    raise KeyError(f"Unknown actor {id_or_name!r}. Registered: {known}")


def get_graph(id_or_name: str) -> Graph:
    if id_or_name in {GENERATOR.id, GENERATOR.name}:
        return GENERATOR.graph()
    return get_actor(id_or_name).graph()


def registry_dict() -> dict[str, Any]:
    return {
        "format": FORMAT,
        "version": FORMAT_VERSION,
        "interface_version": INTERFACE_VERSION,
        "constraint": CONSTRAINT,
        "blender": BLENDER,
        "generator": GENERATOR.to_dict(),
        "states": list(EPOCHS),
        "epochs": "time_slice.EPOCHS",
        "shared": {
            "inputs": list(SHARED_INPUTS) + list(CANON_INPUTS),
            "outputs": list(SHARED_OUTPUTS),
        },
        "materials": [item.to_dict() for item in BINDINGS],
        "groups": [spec.to_dict() for spec in ACTORS],
        "kind": ACTOR_KIND.value,
    }
