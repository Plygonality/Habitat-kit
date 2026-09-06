"""Time-slice epochs as Habitat-kit states. Do not fork Time-slice."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from time_slice.epochs import EPOCH_LABELS, EPOCHS, SCREENSHOT_FOLDERS, EpochId, slice_seed

from habitat_kit.sockets import DECAY_SOCKETS, SIGNAL_SOCKETS

CANONICAL_SEED = 1234
FORMAT = "habitat-kit-state"
FORMAT_VERSION = 1


@dataclass(frozen=True)
class State:
    """One named Habitat Cut. Epoch id is a Time-slice id."""

    id: EpochId
    seed: int = CANONICAL_SEED

    @property
    def epoch(self) -> EpochId:
        return self.id

    @property
    def label(self) -> str:
        return EPOCH_LABELS[self.id]

    @property
    def folder(self) -> str:
        return SCREENSHOT_FOLDERS[self.id]

    def sockets(self) -> dict[str, float]:
        item = slice_seed(self.seed).by_epoch(self.id)
        decay = item.decay.to_dict()
        signal = item.signal.to_dict()
        values: dict[str, float] = {}
        for name, key, _desc in DECAY_SOCKETS:
            values[name] = decay[key]
        for name, key, _desc in SIGNAL_SOCKETS:
            values[name] = signal[key]
        return values

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": FORMAT,
            "version": FORMAT_VERSION,
            "id": self.id,
            "epoch": self.epoch,
            "label": self.label,
            "folder": self.folder,
            "seed": self.seed,
            "source": "time_slice.EPOCHS",
            "sockets": self.sockets(),
        }


STATES: tuple[State, ...] = tuple(State(epoch) for epoch in EPOCHS)
STATES_BY_ID: dict[str, State] = {state.id: state for state in STATES}


def list_states() -> tuple[State, ...]:
    return STATES


def get_state(epoch: str) -> State:
    if epoch not in STATES_BY_ID:
        known = ", ".join(EPOCHS)
        raise KeyError(f"Unknown state {epoch!r}. Time-slice epochs: {known}")
    return STATES_BY_ID[epoch]
