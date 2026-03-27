from __future__ import annotations

from collections import deque
from typing import Deque, Dict, Iterable, List, Optional

import numpy as np

from .station import Station
from .types import RouteId, StationId, TerminalId


class Terminal(Station):
    """
    In short, a Station with two pools to hold Buses: a 'prep' pool and a
    'ready' pool. The first one allow Buses to take their prep time before they
    can be ready to dispatch, and the second one determines which bus to
    dispatch if an agent decides to do so instead of putting that burden on the
    agent. Its methods handle all the logic necessary to make this two-queue
    system work.
    
    """
    def __init__(
        self,
        terminal_id: TerminalId,
        station_id: StationId,
        name: str,
        served_routes: Iterable[RouteId],
        route_to_idx: Dict[RouteId, int],
        q_max_by_route: Dict[RouteId, float],
        demand_by_route: Dict[RouteId, np.ndarray],
        boarding_rate: float = 1.0,
        alight_rate: float = 0.3,
        dwell_ticks: int = 0,
        prep_time_ticks: int = 75, #*Assuming 10-second ticks, that's 12 minutes and a half
        pool_capacity: int = 10, #*Number of buses it can stack at most
        demand_mode: str = "deterministic",
    ):
        """
        Initialize a terminal with prep and ready pools.

        Parameters
        ----------
        terminal_id : TerminalId
            Terminal identifier.
        station_id : StationId
            Station identifier where the terminal is located.
        name : str
            Human-readable name.
        served_routes : Iterable[RouteId]
            Routes served by this terminal station.
        route_to_idx : Dict[RouteId, int]
            Mapping from route id to index in arrays.
        q_max_by_route : Dict[RouteId, float]
            Per-route queue normalization scale.
        demand_by_route : Dict[RouteId, np.ndarray]
            Per-route demand profile array (arrivals per tick).
        boarding_rate : float, optional
            Fraction of queue that can board per tick. Default is 1.0.
        alight_rate : float, optional
            Fraction of onboard passengers that alight per dwell. Default is
            0.3.
        dwell_ticks : int, optional
            Base hold time in ticks. Default is 0.
        prep_time_ticks : int, optional
            Number of ticks a bus spends in prep before ready. Default is 75
            (12 minutes and a half with 10-second ticks).
        pool_capacity : int, optional
            Maximum number of buses the terminal can hold. Default is 10.
        demand_mode : str, optional
            "deterministic" or "poisson". Default is "deterministic".
        """
        super().__init__(
            station_id=station_id,
            name=name,
            served_routes=served_routes,
            route_to_idx=route_to_idx,
            q_max_by_route=q_max_by_route,
            demand_by_route=demand_by_route,
            boarding_rate=boarding_rate,
            alight_rate=alight_rate,
            dwell_ticks=dwell_ticks,
            demand_mode=demand_mode,
            has_bus_pool=True,
        )
        self.terminal_id = terminal_id
        self.pool_capacity = int(pool_capacity)
        self.prep_time_ticks = int(prep_time_ticks)
        self.ready_pool: Deque[int] = deque()
        self.prep_pool: List[tuple[int, int]] = []

    def reset(self) -> None:
        """Clear queues and reset terminal pools.

        Returns
        -------
        None
            This method returns nothing.
        """
        super().reset()
        self.ready_pool.clear()
        self.prep_pool = []

    def accept_bus(self, bus_id: int) -> bool:
        """
        Place a bus into the prep pool if (both ready and prep) pool
        capacity allows.

        Parameters
        ----------
        bus_id : int
            Identifier of the bus arriving at the terminal.

        Returns
        -------
        bool
            True if the bus was accepted, False if the terminal is full.
        """
        if (len(self.ready_pool) + len(self.prep_pool)) >= self.pool_capacity:
            return False
        self.prep_pool.append((bus_id, self.prep_time_ticks))
        return True

    def tick_prep(self) -> list[int]:
        """
        Advance prep timers and move ready buses to the ready pool.

        Returns
        -------
        list[int]
            Bus ids that just became ready.
        """
        ready_now: list[int] = []
        idx = 0
        while idx < len(self.prep_pool):
            bus_id, remaining = self.prep_pool[idx]
            remaining -= 1
            #*Add bus to ready pool if prep time is over
            if remaining <= 0:
                self.ready_pool.append(bus_id)
                self.prep_pool.pop(idx)
                ready_now.append(bus_id)
            #*In case we move a bus to the ready pool, fill in the popped bus'
            #*place with the one that followed
            else:
                self.prep_pool[idx] = (bus_id, remaining)
                idx += 1
        return ready_now

    def dispatch(self, route_id: Optional[RouteId] = None, bus_id: Optional[int] = None) -> Optional[int]:
        """
        Pop the next ready bus for dispatch.

        Parameters
        ----------
        route_id : RouteId, optional
            Route id requested (unused in v0.1 but reserved for routing logic).
        bus_id : int, optional
            Specific bus to dispatch. If provided, the bus is removed from the
            ready pool only if present.

        Returns
        -------
        Optional[int]
            Bus id if available, otherwise None.
        """
        if not self.ready_pool:
            return None
        if bus_id is None:
            return self.ready_pool.popleft()
        try:
            self.ready_pool.remove(bus_id)
        except ValueError:
            return None
        return bus_id
