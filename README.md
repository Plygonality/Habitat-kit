# Habitat-kit

Constraint: every length comes from Unit-canon (meters_per_grid 1.0, deck 3.0, airlock 1.0, figure 1.80); no magic numbers in graphs.

One Geometry Nodes generator instances a brutalist / industrial habitat module from Probe-kit actors. Git is the source of truth. The `.blend` is a cache.

## States

Time-slice epoch IDs. Habitat-kit does not fork Time-slice.

| id | label |
|---|---|
| `construction` | under construction |
| `operational` | operational |
| `relic` | relic |

Example states stay in `graphs/states/` so the kit is demonstrable without a paid pack.

```
Python builder  →  graphs/*.json  →  Plygon-mcp apply  →  viewport
                      ↑
              habitat-kit-registry
```

| Role | Job |
|---|---|
| **This kit** | One generator. Four actors. Three states. |
| **[gn-as-code](https://github.com/Plygonality/gn-as-code)** | Typed builders, canonical JSON, structural diffs |
| **[Probe-kit](https://github.com/Plygonality/Probe-kit)** | Actor contract: Scale, Attach, Hull, Glass |
| **[Unit-canon](https://github.com/Plygonality/Unit-canon)** | meters_per_grid, deck, airlock, figure |
| **[Time-slice](https://github.com/Plygonality/Time-slice)** | `construction` / `operational` / `relic` |
| **[Plygon-mcp](https://github.com/Plygonality/Plygon-mcp)** | Apply the script and screenshot |
| **The `.blend`** | Working cache, never the source of truth |

## Actors

Z-up, Y-forward. Origin is the primary attach. Nested by the one generator; not a second generator.

| id | Group | Role |
|---|---|---|
| `airlock` | HK Airlock | Tube + flange. Diameter = airlock. Depth = grid. |
| `deck_bay` | HK Deck Bay | One-deck shell. Span = deck height. |
| `truss` | HK Truss | Member one deck long. Section from the figure / grids-per-deck. |
| `hatch` | HK Hatch | Circular hatch. Clear opening = airlock diameter. |

## Install

```bash
pip install -e ".[dev]"
python -m habitat_kit list
python -m habitat_kit dump
python -m habitat_kit states
pytest -q
```

Python 3.11+. No Blender required to build, dump, or validate.

```bash
python -m habitat_kit validate
python -m habitat_kit apply-script --all-states --object HabitatModule
python -m habitat_kit dump --check
```

`dump` writes `graphs/`. That JSON is what git diffs. `--check` fails if it is stale.

## Apply in Blender (via Plygon-mcp)

The agent authors graphs here, then asks Plygon-mcp to run a self-contained bpy script. Blender does not need this package installed.

```python
from habitat_kit import to_apply_script

script = to_apply_script(all_states=True, object_name="HabitatModule")
# Plygon-mcp: execute_blender_code(script) → get_viewport_screenshot()
```

The script applies the four actor groups, binds them into `HK Habitat Module`, sets each Time-slice state, and writes `screenshots/<epoch>/viewport.png`.

Create **MN Metal** and **MN Glass** with Master-Node when you have it. The apply script ships free stand-ins so the three states run without a paid pack.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
python -m habitat_kit dump --check
```

```bash
python -m habitat_kit dump   # rewrite graphs/ after an intentional builder change
```

If a dump drifted and the change was not intended, the test failed for a reason.

## Layout

```
src/habitat_kit/        one generator, four actors, Time-slice states
graphs/                 canonical gn-as-code JSON + registry + states
screenshots/            construction / operational / relic (MCP captures)
tests/                  contract, validation, golden dumps, no-magic-numbers
```
