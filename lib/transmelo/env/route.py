from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .types import RouteId, StationId, TerminalId


@dataclass(frozen=True)
class Route:
    """
    A list of Stations with their order and timing parameters.

    Attributes
    ----------
    route_id : RouteId
        Route identifier.
    stations : List[StationId]
        Ordered list of station ids for this route.
    travel_ticks : List[int]
        Ticks between consecutive stations (len = len(stations) - 1).
    extra_dwell_ticks : int
        Extra dwell time added on top of station hold time. Default is 0.
    end_terminal_id : TerminalId
        Terminal id where the route ends.
    """
    route_id: RouteId
    stations: List[StationId]
    travel_ticks: List[int] #*ticks between consecutive stations
    extra_dwell_ticks: int = 0
    end_terminal_id: TerminalId

    def station_index(self, station_id: StationId) -> Optional[int]:
        """
        Return first index where the ID of the Station appears

        Parameters
        ----------
        station_id: StationId
            The Station's ID set in World.
        """
        try:
            return self.stations.index(station_id) 
        except ValueError:
            return None
