from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .types import RouteId, TerminalId


@dataclass
class Bus:
    """
    A collection of general, route, and episode information for a bus.
    """
    #*General info
    bus_id: int
    model_id: int
    capacity: int
    status: str = "READY_IN_POOL"  #*"IN_TRANSIT", "DWELLING", "IN_TERMINAL_PREP", "READY_IN_POOL", "IN_TRANSFER"
    #*DWELLING means at stop

    #*Route info
    route_id: Optional[RouteId] = None
    terminal_id: Optional[TerminalId] = None
    route_pos: Optional[int] = None  #*Current station index if dwelling, last passed if in transit
    next_station_idx: Optional[int] = None
    remaining_ticks: int = 0 #*Before reaching next stop
    dwell_remaining: int = 0 #*Ticks remained for prep/wait at a stop to be over
    pax: int = 0 #*Passengers on board

    #*Episode history
    in_service_ticks: int = 0
    in_prep_ticks: int = 0
    idle_ticks: int = 0
