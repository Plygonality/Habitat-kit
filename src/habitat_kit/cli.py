"""Dump graphs, validate, list states, emit Plygon-mcp apply scripts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gn_as_code.dump import dumps
from gn_as_code.validate import validate

from habitat_kit.apply import to_apply_script
from habitat_kit.registry import ACTORS, GENERATOR, get_graph, registry_dict
from habitat_kit.states import EPOCHS, STATES, get_state

ROOT = Path(__file__).resolve().parents[2]
GRAPHS = ROOT / "graphs"
STATES_DIR = GRAPHS / "states"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="habitat-kit",
        description=(
            "One Geometry Nodes habitat generator. Lengths from Unit-canon. "
            "Actors from Probe-kit. States from Time-slice."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="Print the registry")
    sub.add_parser("states", help="Print the three Time-slice states")

    p_dump = sub.add_parser("dump", help="Write canonical JSON for the generator, actors, and states")
    p_dump.add_argument("-o", "--output", type=Path, default=GRAPHS)
    p_dump.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if graphs/ is stale instead of writing",
    )

    p_val = sub.add_parser("validate", help="Validate the generator and every actor graph")
    p_val.add_argument("id", nargs="?")

    p_apply = sub.add_parser("apply-script", help="Emit a bpy script Plygon-mcp can run")
    p_apply.add_argument("--state", choices=list(EPOCHS), default="operational")
    p_apply.add_argument("--all-states", action="store_true")
    p_apply.add_argument("--object", default="HabitatModule")
    p_apply.add_argument("--out-root", default="screenshots")
    p_apply.add_argument("-o", "--output", type=Path)

    args = parser.parse_args(argv)
    if args.cmd == "list":
        sys.stdout.write(_canonical_json(registry_dict()))
        return 0
    if args.cmd == "states":
        sys.stdout.write(_canonical_json([state.to_dict() for state in STATES]))
        return 0
    if args.cmd == "dump":
        return _dump(args.output, check=args.check)
    if args.cmd == "validate":
        return _validate(args.id)
    if args.cmd == "apply-script":
        script = to_apply_script(
            None if args.all_states else args.state,
            object_name=args.object,
            all_states=args.all_states,
            output_root=args.out_root,
        )
        if args.output:
            args.output.write_text(script, encoding="utf-8")
            sys.stdout.write(f"wrote {args.output}\n")
        else:
            sys.stdout.write(script)
        return 0
    raise AssertionError(args.cmd)


def dump_texts(out: Path) -> dict[str, str]:
    written: dict[str, str] = {"registry.json": _canonical_json(registry_dict())}
    for spec in ACTORS:
        written[f"{spec.id}.json"] = dumps(spec.graph().to_data())
    written[f"{GENERATOR.id}.json"] = dumps(GENERATOR.graph().to_data())
    for state in STATES:
        written[f"states/{state.id}.json"] = _canonical_json(state.to_dict())
    return {name: text for name, text in written.items()}


def _dump(out: Path, *, check: bool) -> int:
    written = dump_texts(out)
    if check:
        stale: list[str] = []
        for name, text in written.items():
            path = out / name
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        if stale:
            sys.stderr.write("stale graphs: " + ", ".join(stale) + "\n")
            sys.stderr.write("Re-run: python -m habitat_kit dump\n")
            return 1
        sys.stdout.write("ok\n")
        return 0

    for name, text in written.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        sys.stdout.write(f"wrote {path}\n")
    return 0


def _validate(id_or_name: str | None) -> int:
    if id_or_name:
        if id_or_name in EPOCHS:
            get_state(id_or_name)
            sys.stdout.write(f"{id_or_name}: ok\n")
            return 0
        graph = get_graph(id_or_name)
        specs = [(id_or_name, graph)]
    else:
        specs = [(spec.id, spec.graph()) for spec in ACTORS]
        specs.append((GENERATOR.id, GENERATOR.graph()))

    failed = 0
    for ident, graph in specs:
        errors = validate(graph.to_data())
        if errors:
            failed += 1
            for err in errors:
                sys.stderr.write(f"{ident}: {err}\n")
        else:
            sys.stdout.write(f"{ident}: ok\n")
    return 2 if failed else 0


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
