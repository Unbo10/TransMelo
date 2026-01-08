from __future__ import annotations

from dataclasses import dataclass

from .types import StationId, TerminalId


@dataclass(frozen=True)
class TerminalSpec:
    """
    Configuration record for building Terminal instances.

    This keeps terminal configuration in BRTConfig without instantiating
    runtime Terminal objects (which hold mutable pools and state).
    """
    terminal_id: TerminalId
    station_id: StationId
    capacity: int
    prep_time_ticks: int
