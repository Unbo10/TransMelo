from __future__ import annotations

from typing import Dict, Iterable, Tuple

import numpy as np

from .types import RouteId, StationId


class Station:
    """
    Station is supposed to serve as the backbone of a Route (which is, inshort, conceived as an ordered list of stations) and as the parent class of
    Terminal. It has all the necessary info for buses to stop (or not) at this
    station, and to board and alight passengers. It also contains useful
    methods to calculate an Station's episode's metrics.
    """
    def __init__(
        self,
        station_id: StationId,
        name: str,
        served_routes: Iterable[RouteId],
        route_to_idx: Dict[RouteId, int],
        q_max_by_route: Dict[RouteId, float],
        demand_by_route: Dict[RouteId, np.ndarray],
        boarding_rate: float = 1.0,
        alight_rate: float = 0.5,
        dwell_ticks: int = 0, #*in ticks
        demand_mode: str = "deterministic",
        has_bus_pool: bool = False
    ):
        """
        Initialize a station with queues, demand, and service parameters.

        Parameters
        ----------
        station_id : StationId
            Station identifier.
        name : str
            Human-readable name.
        served_routes : Iterable[RouteId]
            Routes served by this station.
        route_to_idx : Dict[RouteId, int]
            Mapping from route id to index in arrays.
        q_max_by_route : Dict[RouteId, float]
            Per-route queue normalization scale.
        demand_by_route : Dict[RouteId, np.ndarray]
            Per-route demand array (arrivals per tick).
        boarding_rate : float, optional
            Fraction of queue that can board per tick. Default is 1.0.
        alight_rate : float, optional
            Fraction of onboard passengers that alight per dwell. Default is
            0.5.
        dwell_ticks : int, optional
            Base hold time in ticks. Default is 0.
        demand_mode : str, optional
            "deterministic" or "poisson". Default is "deterministic".
        has_bus_pool : bool, optional
            Whether the station owns a bus pool. Default is False.
        """
        self.station_id: str = station_id
        self.name: str = name or station_id
        self.has_pool: bool = has_bus_pool
        self.route_to_idx = route_to_idx
        self.served_routes: tuple = tuple(served_routes) #*make it immutable to preserve the order
        self.served_indices: Tuple[int, ...] = tuple(
            self.route_to_idx[r] for r in self.served_routes
        ) #*indices of the routes the station serves

        self.queues = np.zeros(len(route_to_idx), dtype=np.int32)
        self.q_max = np.ones(len(route_to_idx), dtype=np.float32)
        for route_id in self.served_routes:
            idx = self.route_to_idx[route_id]
            self.q_max[idx] = max(float(q_max_by_route.get(route_id, 1.0)), 1.0)

        self.demand_mode = demand_mode
        self.demand: Dict[str, np.ndarray] = {} #*route -> array
        for route_id in self.served_routes:
            route_demand = demand_by_route.get(route_id)
            if route_demand is None:
                self.demand[route_id] = np.zeros(1, dtype=np.float32)
            else:
                route_demand = np.asarray(route_demand, dtype=np.float32)
                if route_demand.ndim == 0:
                    route_demand = np.full(1, float(route_demand), dtype=np.float32)
                if route_demand.size == 0:
                    route_demand = np.zeros(1, dtype=np.float32)
                self.demand[route_id] = route_demand

        self.boarding_rate = self._clamp(boarding_rate)
        self.alight_rate = self._clamp(alight_rate)
        self.dwell_ticks = max(0, int(dwell_ticks))

    @staticmethod
    def _clamp(rate: float) -> float:
        """
        Clamp a rate to the [0, 1] range.

        Parameters
        ----------
        rate : float
            Candidate rate value.

        Returns
        -------
        float
            The clamped rate.
        """
        rate = float(rate)
        if rate < 0.0:
            return 0.0
        if rate > 1.0:
            return 1.0
        return rate

    def reset(self) -> None:
        """
        Clear all queues for this station.
        """
        self.queues[:] = 0

    def new_demand_at(self, t: int, rng) -> Dict[RouteId, int]:
        """
        Return new demand to add to each route queue at tick `t`.

        Each route uses its demand at `t` as the mean. In `deterministic`
        mode, it returns the value directly; in `poisson` mode, it samples
        demand from a Poisson distribution with that mean.

        Parameters
        ----------
        t : int
            Tick index.
        rng : np.random.Generator
            Random number generator with a poisson method.

        Returns
        -------
        Dict[RouteId, int]
            Mapping from route id to demand at tick t.
        """
        demand: Dict[RouteId, int] = {}
        for route_id in self.served_routes:
            route_demand = self.demand[route_id] #*get route
            rate = float(route_demand[t]) if t < route_demand.size else 0.0 #*get route's demand
            if self.demand_mode == "poisson":
                demand[route_id] = int(rng.poisson(rate))
            else:
                demand[route_id] = int(round(rate))
        return demand

    def add_demand(self, demand: Dict[RouteId, int]) -> None:
        """
        Adds new demand (new users arriving to the station) to the per-route
        queues.

        Parameters
        ----------
        demand : Dict[RouteId, int]
            Mapping from route id to demand to add.

        Notes
        -----
        `demand` expected from `new_demand_at`.
        """
        for route_id, count in demand.items():
            if route_id not in self.route_to_idx:
                continue
            idx = self.route_to_idx[route_id]
            self.queues[idx] += int(count)

    def board(self, bus, route_id: RouteId) -> tuple[int, int]:
        """
        Board passengers for a route.

        Parameters
        ----------
        bus : Bus
            Bus object with capacity and pax attributes.
        route_id : RouteId
            Route id being served.

        Returns
        -------
        tuple[int, int]
            (boarded, denied_or_leftover).
        """
        if route_id not in self.route_to_idx:
            return 0, 0 #*a route not served by the station can't pick up nor leave behind any user
        
        idx = self.route_to_idx[route_id]
        queue_len = int(self.queues[idx])
        free_cap = max(0, int(bus.capacity - bus.pax))

        if queue_len == 0 or free_cap == 0:
            return 0, queue_len #*not 0 to consider the case when free_cap is 0 but queue_len is not
        
        max_board = int(np.ceil(queue_len * self.boarding_rate)) #*per tick
        boarded = min(queue_len, free_cap, max_board)
        self.queues[idx] = queue_len - boarded
        bus.pax += boarded
        denied = max(0, queue_len - free_cap) #*not 0 when bus is full and/or towards the end of the boarding process
        return boarded, denied

    def alight(self, bus) -> int:
        """
        Remove a fraction of onboard passengers.

        Parameters
        ----------
        bus : Bus
            Bus object with pax attribute.

        Returns
        -------
        int
            Number of passengers that alighted.
        """
        if bus.pax == 0:
            return 0
        alight = int(round(bus.pax * self.alight_rate))
        bus.pax -= alight
        return alight

    def q_norm(self, route_id: RouteId, eps: float = 1e-6) -> float:
        """
        Return normalized queue length for a route, capped at 1.0.

        Parameters
        ----------
        route_id : RouteId
            Route id to normalize.
        eps : float, optional
            Small value to avoid division by zero.

        Returns
        -------
        float
            Normalized queue length.
        """
        if route_id not in self.route_to_idx:
            return 0.0
        idx = self.route_to_idx[route_id]
        norm = float(self.queues[idx]) / float(self.q_max[idx] + eps)
        return min(norm, 1.0)

    def total_queue(self) -> int:
        """
        Return total queue length across all served routes.

        Returns
        -------
        int
            Sum of queues over served routes.
        """
        if not self.served_indices:
            return 0
        return int(self.queues[list(self.served_indices)].sum())

    def q_max_total(self) -> float:
        """
        Return total q_max (max queue during a certain period of time across
        the entire dataset's 'duration') across all served routes.

        Returns
        -------
        float
            Sum of q_max over served routes.
        """
        if not self.served_indices:
            return 0.0
        return float(self.q_max[list(self.served_indices)].sum())
