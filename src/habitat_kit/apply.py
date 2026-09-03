"""Plygon-mcp apply script: nested actor groups, one generator, then screenshot.

Blender does not need this package installed. The script embeds gn-as-code
runtime plus Habitat-kit dumps. The .blend is a cache.
"""

from __future__ import annotations

import json

from gn_as_code.apply import _RUNTIME_PATH
from gn_as_code.dump import to_dict
from unit_canon.load import load

from habitat_kit.registry import ACTORS, GENERATOR
from habitat_kit.states import EPOCHS, STATES, State, get_state

OBJECT_NAME = "HabitatModule"
MODIFIER_NAME = "GeometryNodes"


def graphs_payload() -> list[dict]:
    payload = [to_dict(spec.graph().to_data()) for spec in ACTORS]
    payload.append(to_dict(GENERATOR.graph().to_data()))
    return payload


def canon_payload() -> dict[str, float]:
    item = load()
    return {
        "meters_per_grid": item.meters_per_grid,
        "deck_height": item.deck_height,
        "airlock_diameter": item.airlock_diameter,
        "human_standing_height": item.human_figure.standing_height,
        "human_eye_height": item.human_figure.eye_height,
        "human_shoulder_width": item.human_figure.shoulder_width,
    }


def to_apply_script(
    state: str | State | None = None,
    *,
    object_name: str = OBJECT_NAME,
    all_states: bool = False,
    output_root: str = "screenshots",
) -> str:
    """Self-contained bpy. Plygon-mcp: execute_blender_code(this) → screenshot."""
    if all_states:
        epochs = list(EPOCHS)
    elif state is None:
        epochs = ["operational"]
    else:
        resolved = state if isinstance(state, State) else get_state(state)
        epochs = [resolved.id]

    states = {item.id: item.to_dict() for item in STATES}
    runtime = _RUNTIME_PATH.read_text(encoding="utf-8")
    runner = _RUNNER.format(
        graphs=json.dumps(graphs_payload()),
        states=json.dumps(states),
        canon=json.dumps(canon_payload()),
        epochs=repr(epochs),
        object_name=repr(object_name),
        modifier_name=repr(MODIFIER_NAME),
        output_root=repr(output_root),
        generator_name=repr(GENERATOR.name),
    )
    return runtime + "\n\n" + runner


_RUNNER = '''\
# Habitat-kit apply. Generated. Plygon-mcp: execute_blender_code(this).
# Apply actor groups, bind them into the one generator, set a Time-slice state, screenshot.

import json
import math
from pathlib import Path

import bpy

GRAPHS = json.loads({graphs!r})
STATES = json.loads({states!r})
CANON = json.loads({canon!r})
EPOCH_IDS = {epochs}
OBJECT_NAME = {object_name}
MODIFIER_NAME = {modifier_name}
OUTPUT_ROOT = Path({output_root})
GENERATOR_NAME = {generator_name}


def apply_habitat_graph(data, bpy_mod, *, object_name=None, modifier_name="GeometryNodes", replace=True):
    _validate_payload(data)
    name = data["name"]
    tree = bpy_mod.data.node_groups.get(name)
    if tree is None:
        tree = bpy_mod.data.node_groups.new(name, "GeometryNodeTree")
    elif not replace:
        raise ValueError("Node group %r already exists" % name)
    _set_kind(tree, data.get("kind", "MODIFIER"))
    _clear_tree(tree)
    _build_interface(tree, data.get("interface") or {{}})
    created = _build_nodes(tree, data.get("nodes") or [])
    _bind_nested_groups(created, bpy_mod, data.get("nodes") or [])
    _build_links(tree, data.get("links") or [], created)
    if object_name:
        _attach_modifier(bpy_mod, object_name, tree, modifier_name)
    return tree


def _bind_nested_groups(created, bpy_mod, specs):
    for spec in specs:
        if spec.get("type") != "GeometryNodeGroup":
            continue
        node = created.get(spec["id"])
        if node is None:
            continue
        target_name = spec.get("label") or (spec.get("properties") or {{}}).get("node_tree")
        if not target_name:
            continue
        target = bpy_mod.data.node_groups.get(target_name)
        if target is None:
            raise KeyError("Nested group %r not applied yet" % target_name)
        node.node_tree = target


def _material(name, color, roughness, metallic, transmission=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = transmission
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def _set_interface_defaults(tree, values, materials):
    iface = getattr(tree, "interface", None)
    if iface is None:
        return
    for item in list(getattr(iface, "items_tree", [])):
        if getattr(item, "in_out", None) != "INPUT":
            continue
        if item.name in materials and hasattr(item, "default_value"):
            try:
                item.default_value = materials[item.name]
            except Exception:
                pass
        if item.name in values and hasattr(item, "default_value"):
            try:
                item.default_value = values[item.name]
            except Exception:
                pass


def _ensure_camera_and_light():
    deck = float(CANON["deck_height"])
    grid = float(CANON["meters_per_grid"])
    cam_data = bpy.data.cameras.new("Habitat.Camera")
    cam = bpy.data.objects.new("Habitat.Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = (deck + deck, -(deck + deck), deck + grid)
    cam.rotation_euler = (math.radians(62), 0.0, math.radians(35))
    cam_data.lens = 35
    bpy.context.scene.camera = cam

    sun_data = bpy.data.lights.new("Habitat.Sun", "SUN")
    sun = bpy.data.objects.new("Habitat.Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(40), math.radians(15), math.radians(30))
    sun_data.energy = 4.0

    key_data = bpy.data.lights.new("Habitat.Key", "AREA")
    key = bpy.data.objects.new("Habitat.Key", key_data)
    bpy.context.scene.collection.objects.link(key)
    key.location = (deck + grid, -deck, deck)
    key_data.energy = 180.0
    key_data.size = deck

    world = bpy.context.scene.world or bpy.data.worlds.new("Habitat.World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.02, 0.022, 0.03, 1.0)
        bg.inputs["Strength"].default_value = 0.35


def _clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def apply_state(epoch_id):
    spec = STATES[epoch_id]
    tree = bpy.data.node_groups.get(GENERATOR_NAME)
    hull = _material("MN Metal", (0.22, 0.23, 0.24, 1.0), 0.35, 0.85)
    glass = _material("MN Glass", (0.35, 0.55, 0.62, 1.0), 0.05, 0.0, transmission=0.9)
    _set_interface_defaults(tree, spec["sockets"], {{"Hull": hull, "Glass": glass}})
    oxidation = float(spec["sockets"].get("Oxidation", 0.0))
    sun = bpy.data.objects.get("Habitat.Sun")
    if sun and sun.data:
        sun.data.energy = 2.2 if epoch_id == "relic" else 4.5 if epoch_id == "operational" else 3.2
    hull.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.25 + 0.55 * oxidation
    return spec


def shoot(epoch_id):
    apply_state(epoch_id)
    folder = OUTPUT_ROOT / epoch_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "viewport.png"
    scene = bpy.context.scene
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.opengl(write_still=True)
    return str(path)


def run():
    _clear_scene()
    for data in GRAPHS:
        object_name = OBJECT_NAME if data["name"] == GENERATOR_NAME else None
        apply_habitat_graph(
            data,
            bpy,
            object_name=object_name,
            modifier_name=MODIFIER_NAME,
            replace=True,
        )
    _ensure_camera_and_light()
    written = [shoot(epoch_id) for epoch_id in EPOCH_IDS]
    print("habitat-kit wrote:", ", ".join(written))
    return written


if __name__ == "__main__":
    run()
'''
