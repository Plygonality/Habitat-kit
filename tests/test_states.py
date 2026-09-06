from __future__ import annotations

from time_slice.epochs import EPOCH_LABELS, EPOCHS, SCREENSHOT_FOLDERS, slice_seed

from habitat_kit.sockets import EPOCH_SOCKET_NAMES
from habitat_kit.states import CANONICAL_SEED, STATES, get_state, list_states


def test_states_are_time_slice_epoch_ids() -> None:
    assert tuple(state.id for state in STATES) == EPOCHS
    assert EPOCHS == ("construction", "operational", "relic")
    assert [state.id for state in list_states()] == list(EPOCHS)


def test_state_labels_and_folders_come_from_time_slice() -> None:
    for state in STATES:
        assert state.label == EPOCH_LABELS[state.id]
        assert state.folder == SCREENSHOT_FOLDERS[state.id]
        assert state.folder == f"screenshots/{state.id}"


def test_state_sockets_match_canonical_time_slice_seed() -> None:
    slices = slice_seed(CANONICAL_SEED)
    for state in STATES:
        item = slices.by_epoch(state.id)
        sockets = state.sockets()
        decay = item.decay.to_dict()
        signal = item.signal.to_dict()
        assert set(sockets) == set(EPOCH_SOCKET_NAMES)
        assert sockets["Incomplete"] == decay["incomplete"]
        assert sockets["Scaffold"] == decay["scaffold"]
        assert sockets["Oxidation"] == decay["oxidation"]
        assert sockets["Breach"] == decay["breach"]
        assert sockets["Debris"] == decay["debris"]
        assert sockets["Density"] == signal["density"]
        assert sockets["Ghost"] == signal["ghost"]


def test_generator_exposes_epoch_sockets() -> None:
    from habitat_kit.generator import build_habitat_module

    names = {item.name for item in build_habitat_module().to_data().interface_inputs}
    for socket in EPOCH_SOCKET_NAMES:
        assert socket in names


def test_get_state_rejects_forked_ids() -> None:
    try:
        get_state("under_construction")
    except KeyError as err:
        assert "construction" in str(err)
    else:
        raise AssertionError("expected KeyError")
