from __future__ import annotations

from unit_canon.gn_as_code import defaults

from habitat_kit.canon import canon


def test_canon_measures_match_unit_canon_file() -> None:
    item = canon()
    values = defaults()
    assert item.meters_per_grid == 1.0
    assert item.deck_height == 3.0
    assert item.airlock_diameter == 1.0
    assert item.human_figure.standing_height == 1.8
    assert values["meters_per_grid"] == item.meters_per_grid
    assert values["deck_height"] == item.deck_height
    assert values["airlock_diameter"] == item.airlock_diameter
    assert values["human_figure.standing_height"] == item.human_figure.standing_height
