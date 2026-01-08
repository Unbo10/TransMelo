from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from .bus import Bus
from .config import BRTConfig
from .route import Route
from .station import Station
from .terminal import Terminal
from .terminal_spec import TerminalSpec
from .types import RouteId, StationId, TerminalId


class World:
    """
    Discrete-time simulator for the BRT environment.

    Manages stations, terminals, buses, queues, and event ordering for each
    tick. Exposes helper methods to build observations and compute rewards.
    """
    def __init__(self, config: BRTConfig):
        """
        Initialize the world state and derived structures.

        Parameters
        ----------
        config : BRTConfig
            Environment configuration.
        """
        #*Getting stuff from config
        self.config: BRTConfig = config
        self.rng = np.random.default_rng(config.rng_seed)
        self.routes = {route.route_id: route for route in config.routes}
        self.route_order = [route.route_id for route in config.routes]
        self.route_to_idx = {route_id: idx for idx, route_id in enumerate(self.route_order)}
        self.terminal_order = [terminal.terminal_id for terminal in config.terminals]
        self.route_endpoints = config.route_endpoints
        self.terminal_transfer_times = config.terminal_transfer_times
        self.terminal_spec_by_station: Dict[StationId, TerminalSpec] = {}
        self.terminal_id_by_station: Dict[StationId, TerminalId] = {}
        self.dispatch_options: Dict[TerminalId, List[Tuple[RouteId, StationId, int]]] = {}
        self.transfer_options: Dict[TerminalId, List[Tuple[TerminalId, int]]] = {}

        #*Episode info
        self.t = 0
        self.time_sec = 0.0
        self.buses: List[Bus] = []
        self.stations: Dict[StationId, Station] = {}
        self.terminals: Dict[TerminalId, Terminal] = {}
        self.bus_end_idx: Dict[int, Optional[int]] = {}
        self.last_departure: Dict[RouteId, Optional[int]] = {}
        self.headways: Dict[RouteId, List[int]] = {}
        self.completed_routes: Dict[RouteId, int] = {}
        self.completed_routes_total = 0
        self.q_max_total = 0.0
        self.transfer_queue: List[Tuple[int, TerminalId, TerminalId, int]] = []

        self._build_stations()

    def _build_stations(self) -> None:
        """
        Instantiate Station and Terminal objects from configuration, attempting
        to get their demands and max queues per route from `demand_by_route`
        and `q_max_by_route`, and falling back to `config`'s defaults if it
        fails.
        """
        #*1) Create the map station -> routes it serves
        station_routes: Dict[StationId, List[RouteId]] = {}
        for route_id, route in self.routes.items():
            for station_id in route.stations:
                routes = station_routes.setdefault(station_id, [])
                if route_id not in routes:
                    routes.append(route_id)

        terminal_spec_by_station: Dict[StationId, TerminalSpec] = {spec.station_id: spec for spec in self.config.terminals} #*config.terminals contains TerminalSpecs
        self.terminal_spec_by_station = terminal_spec_by_station
        self.terminal_id_by_station = {spec.station_id: spec.terminal_id for spec in self.config.terminals}
        t_max = int(round(20 * 60 / self.config.dt_sec)) #*window length for ETA normalization
        horizon_len = max(int(self.config.horizon_ticks), 1) #*or episode length

        #*2) Initialize Terminal or Station with their demands and max queue
        #*per route
        for station_id, served_routes in station_routes.items():
            q_max_by_route: Dict[RouteId, float] = {}
            demand_by_route: Dict[RouteId, np.ndarray] = {}
            station_demand = self.config.demand_by_route.get(station_id, {})
            station_q_max = self.config.q_max_by_route.get(station_id, {})

            #*Get each station's served route demand from config or fill it
            #*with base demand rate. If it is a scalar (so average rate), leave 
            #*it as such inside a np array
            for route_id in served_routes:
                route_demand = station_demand.get(route_id)
                if route_demand is not None and len(route_demand) > 0:
                    route_demand_arr = np.asarray(route_demand, dtype=np.float32)
                    if route_demand_arr.ndim == 0: #*scalar
                        route_demand_arr = np.full(1, float(route_demand_arr), dtype=np.float32)
                    demand_by_route[route_id] = route_demand_arr
                    base_rate = float(route_demand_arr.mean())
                else: #*empty or not provided -> use base demand rate
                    base_rate = self.config.demand_rates.get(route_id, {}).get(station_id, 0.0)
                    demand_by_route[route_id] = np.full(horizon_len, base_rate, dtype=np.float32)

                if route_id in station_q_max:
                    q_max_by_route[route_id] = max(float(station_q_max[route_id]), 1.0)
                else:
                    q_max_by_route[route_id] = max(base_rate * t_max, 1.0)

            #*Get boarding, alight and dwell info or default to config's value
            boarding_rate = self.config.station_boarding_rates.get(
                station_id, self.config.default_boarding_rate
            )
            alight_rate = self.config.station_alight_rates.get(
                station_id, self.config.default_alight_rate
            )
            dwell_ticks = self.config.station_hold_times.get(
                station_id, self.config.default_station_hold_ticks
            )

            #*Initialize Terminal or Station
            if station_id in terminal_spec_by_station:
                spec = terminal_spec_by_station[station_id]
                terminal = Terminal(
                    terminal_id=spec.terminal_id,
                    station_id=station_id,
                    name=station_id,
                    served_routes=served_routes,
                    route_to_idx=self.route_to_idx,
                    q_max_by_route=q_max_by_route,
                    demand_by_route=demand_by_route,
                    boarding_rate=boarding_rate,
                    alight_rate=alight_rate,
                    dwell_ticks=dwell_ticks,
                    prep_time_ticks=spec.prep_time_ticks,
                    capacity=spec.capacity,
                    demand_mode=self.config.demand_mode,
                )
                self.terminals[spec.terminal_id] = terminal
                self.stations[station_id] = terminal
            else:
                station = Station(
                    station_id=station_id,
                    name=station_id,
                    served_routes=served_routes,
                    route_to_idx=self.route_to_idx,
                    q_max_by_route=q_max_by_route,
                    demand_by_route=demand_by_route,
                    boarding_rate=boarding_rate,
                    alight_rate=alight_rate,
                    dwell_ticks=dwell_ticks,
                    demand_mode=self.config.demand_mode,
                )
                self.stations[station_id] = station

        self.q_max_total = sum(station.q_max_total() for station in self.stations.values())
        self._build_dispatch_options()
        self._build_transfer_options()

    def _build_dispatch_options(self) -> None:
        """
        Build dispatch options per terminal based on route endpoints.
        """
        self.dispatch_options = {}
        for terminal_id in self.terminal_order:
            terminal = self.terminals.get(terminal_id)
            if terminal is None:
                continue
            start_station = terminal.station_id
            options: List[Tuple[RouteId, StationId, int]] = []
            for route_id in self.config.terminal_routes.get(terminal_id, []):
                route = self.routes.get(route_id)
                if route is None:
                    continue
                start_idx = route.station_index(start_station)
                if start_idx is None:
                    continue
                endpoints = self.route_endpoints.get(route_id, [route.stations[-1]])
                for endpoint_station in endpoints:
                    end_idx = route.station_index(endpoint_station)
                    if end_idx is None:
                        continue
                    if end_idx <= start_idx:
                        continue
                    if endpoint_station not in self.terminal_id_by_station:
                        continue
                    options.append((route_id, endpoint_station, end_idx))
            self.dispatch_options[terminal_id] = options

    def _build_transfer_options(self) -> None:
        """
        Build transfer options from `terminal_transfer_times`. Each option is a
        pair (End Terminal, travel ticks) keyed by start terminal.
        """
        options: Dict[TerminalId, List[Tuple[TerminalId, int]]] = {}
        for from_terminal in self.terminal_order:
            terminal_opts: List[Tuple[TerminalId, int]] = []
            dests = self.terminal_transfer_times.get(from_terminal, {})
            for to_terminal, travel_ticks in dests.items():
                if to_terminal == from_terminal:
                    continue
                if to_terminal not in self.terminals:
                    continue
                travel_ticks = int(travel_ticks)
                if travel_ticks < 0:
                    continue
                terminal_opts.append((to_terminal, travel_ticks))
            options[from_terminal] = terminal_opts
        self.transfer_options = options

    def reset(self, seed: Optional[int] = None) -> None:
        """
        Reset world state and optionally reseed RNG.

        Parameters
        ----------
        seed : int, optional
            RNG seed to use for this reset. Default is None.
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self.t = 0
        self.time_sec = 0.0
        self.buses = [Bus(bus_id=i, capacity=self.config.bus_capacity) for i in range(self.config.fleet_size)]
        for station in self.stations.values():
            station.reset() #*clear current queues
        for terminal in self.terminals.values():
            terminal.reset()

        self.last_departure = {route_id: None for route_id in self.routes}
        self.headways = {route_id: [] for route_id in self.routes}
        self.completed_routes = {route_id: 0 for route_id in self.routes}
        self.completed_routes_total = 0
        self.bus_end_idx = {}
        self.transfer_queue = []

        if not self.terminal_order:
            return

        for idx, bus in enumerate(self.buses):
            terminal_id = self.terminal_order[idx % len(self.terminal_order)]
            terminal = self.terminals[terminal_id]
            bus.status = "READY_IN_POOL"
            bus.terminal_id = terminal_id
            bus.route_id = None
            bus.route_pos = None
            bus.next_station_idx = None
            bus.remaining_ticks = 0
            bus.dwell_remaining = 0
            bus.pax = 0
            self.bus_end_idx[bus.bus_id] = None
            terminal.ready_pool.append(bus.bus_id)

    def get_action_mask(self) -> List[np.ndarray]:
        """
        Return action masks for dispatch and transfer components.

        Returns
        -------
        List[np.ndarray]
            List of masks for each MultiDiscrete component (dispatch per
            terminal, then transfer per terminal in the same order).
        """
        masks: List[np.ndarray] = []
        #*Dispatch masks
        for terminal_id in self.terminal_order:
            terminal = self.terminals[terminal_id]
            options = self.dispatch_options.get(terminal_id, []) #*route options
            dispatch_term_mask = np.zeros(len(options) + 1, dtype=np.int8)
            dispatch_term_mask[0] = 1
            if terminal.ready_pool and options:
                dispatch_term_mask[1:] = 1
            masks.append(dispatch_term_mask)

        #*Transfer masks (moving a bus to another terminal)
        for terminal_id in self.terminal_order:
            terminal = self.terminals[terminal_id]
            options = self.transfer_options.get(terminal_id, []) #*transfer options
            transfer_mask = np.zeros(len(options) + 1, dtype=np.int8)
            transfer_mask[0] = 1
            for idx, (to_terminal_id, _) in enumerate(options):
                to_terminal = self.terminals.get(to_terminal_id)
                if to_terminal is None:
                    continue
                if not terminal.ready_pool:
                    continue
                #*Block if end Terminal's pool is full
                if (len(to_terminal.ready_pool) + len(to_terminal.prep_pool)) >= to_terminal.pool_capacity:
                    continue
                transfer_mask[idx + 1] = 1
            masks.append(transfer_mask)
        return masks

    def _dispatch_bus(
        self,
        terminal_id: TerminalId,
        route_id: RouteId,
        end_station_id: StationId,
        end_idx: int,
    ) -> bool:
        """
        Dispatch a ready bus from a terminal onto a route.

        Parameters
        ----------
        terminal_id : TerminalId
            Terminal to dispatch from.
        route_id : RouteId
            Route to assign.
        end_station_id : StationId
            Endpoint station for this run.
        end_idx : int
            Index of the endpoint station in the route.

        Returns
        -------
        bool
            True if a bus was dispatched, False otherwise.
        """
        #*1) Check if the route is served by the terminal and if the terminal
        #*appears in and is not the last stop of the route
        if route_id not in self.config.terminal_routes.get(terminal_id, []):
            return False
        terminal = self.terminals[terminal_id]
        if not terminal.ready_pool:
            return False

        route = self.routes[route_id]
        start_idx = route.station_index(terminal.station_id)
        if start_idx is None or start_idx >= len(route.stations) - 1: #*not found or it is last stop
            return False
        if end_station_id != route.stations[end_idx]:
            return False
        if end_idx <= start_idx:
            return False

        bus_id = terminal.dispatch(route_id) #*remove from ready pool
        if bus_id is None:
            return False

        bus = self.buses[bus_id]
        bus.route_id = route_id
        bus.status = "IN_TRANSIT"
        bus.terminal_id = None
        bus.route_pos = start_idx
        bus.next_station_idx = start_idx + 1
        self.bus_end_idx[bus_id] = end_idx
        bus.remaining_ticks = route.travel_ticks[start_idx]
        bus.dwell_remaining = 0

        last_dep = self.last_departure.get(route_id)
        #*Update headway
        if last_dep is not None:
            gap = self.t - last_dep
            self.headways[route_id].append(gap)
            if len(self.headways[route_id]) > self.config.headway_window: #*make sure the window is the same size always
                self.headways[route_id] = self.headways[route_id][-self.config.headway_window :]
        self.last_departure[route_id] = self.t
        return True

    def step_tick(self, action: np.ndarray) -> Dict[str, int]:
        """
        Advance the world by one tick.

        Parameters
        ----------
        action : np.ndarray
            MultiDiscrete action array.

        Returns
        -------
        Dict[str, int]
            Per-tick metrics.
        """
        return self.tick(action)

    def tick(self, action: np.ndarray) -> Dict[str, int]:
        """
        Advance the world by one tick with the given action.

        Parameters
        ----------
        action : np.ndarray
            MultiDiscrete action array.

        Returns
        -------
        Dict[str, int]
            Per-tick metrics for reward and logging.
        """
        metrics = {
            "boarded": 0,
            "denied": 0,
            "dispatches": 0,
            "bus_transfers": 0,
            "invalid_actions": 0,
            "completed_routes": 0,
            "completed_by_route": {route_id: 0 for route_id in self.routes},
        }

        #*1) Update demand of each station (new users entering the queues)
        for station in self.stations.values():
            new_demand = station.new_demand_at(self.t, self.rng)
            station.add_demand(new_demand)

        #*2) Update buses ...
        #*2.1) For each bus in transit (i.e., has a route but it is not at a
        #*station), subtract one tick to the remaining ones till next stop, and
        #*set to 'dwelling mode' if it arrived to the stop
        newly_arrived: set[int] = set()
        for bus in self.buses:
            if bus.status != "IN_TRANSIT" or bus.route_id is None:
                continue
            bus.remaining_ticks -= 1
            if bus.remaining_ticks > 0:
                continue
            #*Set dwelling mode
            route = self.routes[bus.route_id]
            bus.status = "DWELLING"
            bus.route_pos = bus.next_station_idx
            bus.next_station_idx = None
            station_id = route.stations[bus.route_pos]
            station = self.stations[station_id]
            bus.dwell_remaining = route.extra_dwell_ticks + station.dwell_ticks
            newly_arrived.add(bus.bus_id)

        #*2.2) For each bus at a stop (dwelling mode)
        for bus in self.buses:
            #*Boarding/Alighiting at a stop of an active route
            if bus.status != "DWELLING" or bus.route_id is None or bus.route_pos is None:
                continue
            if bus.bus_id in newly_arrived:
                continue
            route = self.routes[bus.route_id]
            station_id = route.stations[bus.route_pos]
            station = self.stations[station_id]

            #*Alight and board simultaneously
            station.alight(bus)
            boarded, denied = station.board(bus, bus.route_id)
            metrics["boarded"] += boarded
            metrics["denied"] += denied

            bus.dwell_remaining -= 1
            if bus.dwell_remaining > 0:
                continue

            #*Only if dwell is over, update episode route-related metrics, add
            #*bus to pool, and reset bus config
            end_idx = self.bus_end_idx.get(bus.bus_id, len(route.stations) - 1)
            if bus.route_pos == end_idx:
                #*Update metrics
                completed_route_id = bus.route_id
                if completed_route_id is not None:
                    metrics["completed_routes"] += 1
                    metrics["completed_by_route"][completed_route_id] += 1
                    self.completed_routes[completed_route_id] += 1
                    self.completed_routes_total += 1

                #*Add the bus to the Terminal pool. If the ending station
                #*is not a Terminal, throws an error
                end_station = route.stations[end_idx]
                terminal_id = self.terminal_id_by_station.get(end_station)
                if terminal_id is None:
                    raise RuntimeError(
                        f"Endpoint station '{end_station}' for route '{route.route_id}' has no terminal."
                    )
                else:
                    terminal = self.terminals[terminal_id]
                    terminal.accept_bus(bus.bus_id)
                    bus.status = "IN_TERMINAL_PREP"
                    bus.terminal_id = terminal_id

                #*Resetting bus. Guarantees metrics updated just once
                bus.route_id = None
                bus.route_pos = None
                bus.next_station_idx = None
                bus.remaining_ticks = 0
                bus.pax = 0
                self.bus_end_idx[bus.bus_id] = None
                continue

            #*If it reaches this point, dwell is over, so back to in-transit
            #*Unless it is last stop, in which case, falls into previous if
            bus.status = "IN_TRANSIT"
            bus.next_station_idx = bus.route_pos + 1
            bus.remaining_ticks = route.travel_ticks[bus.route_pos]

        #*2.3) Update buses transferring from one terminal to another
        idx = 0
        while idx < len(self.transfer_queue):
            bus_id, from_terminal_id, to_terminal_id, remaining_ticks = self.transfer_queue[idx]
            remaining_ticks -= 1
            if remaining_ticks == 0: #*arrived to the destination terminal
                dest_terminal = self.terminals.get(to_terminal_id)
                if dest_terminal is None:
                    raise RuntimeError(
                        f"Transfer destination terminal '{to_terminal_id}' not found."
                    )
                if dest_terminal.accept_bus(bus_id): #*enter prep pool
                    bus = self.buses[bus_id]
                    bus.status = "IN_TERMINAL_PREP"
                    bus.terminal_id = dest_terminal.terminal_id
                    self.transfer_queue.pop(idx)
                else: #*if bus is rejected, leaves it in queue to retry in the next tick
                    self.transfer_queue[idx] = (bus_id, from_terminal_id, to_terminal_id, 1)
            else: #*simply update the queue with remaining ticks for this bus
                self.transfer_queue[idx] = (bus_id, from_terminal_id, to_terminal_id, remaining_ticks)
            idx += 1

        #*3)Update Terminal's pools
        for terminal in self.terminals.values():
            terminal.tick_prep()
            # for bus_id, _ in terminal.prep_pool: #*Handled in 2.3; deemed redundant
            #     self.buses[bus_id].status = "IN_TERMINAL_PREP"
            #     self.buses[bus_id].terminal_id = terminal.terminal_id
            for bus_id in terminal.ready_pool:
                self.buses[bus_id].status = "READY_IN_POOL"
                self.buses[bus_id].terminal_id = terminal.terminal_id

        #*4) Action parsing
        action_arr = np.asarray(action, dtype=int)
        expected_size = len(self.terminal_order) * 2 #*dispatch and transfer per terminal
        if action_arr.size != expected_size:
            raise ValueError(
                f"Action has size {action_arr.size}, expected {expected_size} "
                f"(dispatch + transfer per terminal)."
            )
        dispatch_actions = action_arr[: len(self.terminal_order)]
        transfer_actions = action_arr[len(self.terminal_order) :]

        #*4.1) Execute or reject Terminal dispatch actions
        for terminal_id, act in zip(self.terminal_order, dispatch_actions):
            if act == 0: #*no action at this Terminal
                continue
            options = self.dispatch_options.get(terminal_id, [])
            option_idx = int(act) - 1
            if option_idx < 0 or option_idx >= len(options): #*invalid
                metrics["invalid_actions"] += 1
                continue
            #*Requestispatch at this Terminal
            route_id, end_station_id, end_idx = options[option_idx]
            accepted_dispatch = self._dispatch_bus(terminal_id, route_id, end_station_id, end_idx)
            if accepted_dispatch:
                metrics["dispatches"] += 1
            else:
                metrics["invalid_actions"] += 1

        #*4.2) Execute or reject transfer actions (per terminal)
        for terminal_id, act in zip(self.terminal_order, transfer_actions):
            if act == 0:
                continue
            options = self.transfer_options.get(terminal_id, [])
            option_idx = int(act) - 1
            if option_idx < 0 or option_idx >= len(options):
                metrics["invalid_actions"] += 1
                continue
            to_terminal_id, travel_ticks = options[option_idx]
            from_terminal = self.terminals.get(terminal_id)
            to_terminal = self.terminals.get(to_terminal_id)
            if from_terminal is None or to_terminal is None: #*invalid terminals
                metrics["invalid_actions"] += 1
            elif not from_terminal.ready_pool: #*empty ready pool
                metrics["invalid_actions"] += 1
            elif (len(to_terminal.ready_pool) + len(to_terminal.prep_pool)) >= to_terminal.pool_capacity: #*destination terminal cannot accept incoming bus
                metrics["invalid_actions"] += 1
            else:
                bus_id = from_terminal.dispatch()
                if bus_id is None: #*safeguard: empty ready pool
                    metrics["invalid_actions"] += 1
                else:
                    self.transfer_queue.append(
                        (bus_id, terminal_id, to_terminal_id, int(travel_ticks))
                    )
                    bus = self.buses[bus_id]
                    bus.status = "IN_TRANSFER"
                    bus.terminal_id = None
                    bus.route_id = None
                    bus.route_pos = None
                    bus.next_station_idx = None
                    bus.remaining_ticks = 0
                    bus.dwell_remaining = 0
                    bus.pax = 0
                    self.bus_end_idx[bus_id] = None
                    metrics["bus_transfers"] += 1

        #*5) Update time
        self.t += 1
        self.time_sec += self.config.dt_sec
        return metrics

    def _eta_to_station(self, bus: Bus, route: Route, station_idx: int) -> Optional[int]:
        """Compute ETA in ticks for a bus to reach a station index.

        Parameters
        ----------
        bus : Bus
            Bus to evaluate.
        route : Route
            Route the bus is serving.
        station_idx : int
            Index into route.stations.

        Returns
        -------
        Optional[int]
            ETA in ticks, or None if not reachable.
        """
        #*Make sure the requested station is located before the last one
        end_idx = self.bus_end_idx.get(bus.bus_id)
        if end_idx is not None and station_idx > end_idx:
            return None
        
        if bus.status == "IN_TRANSIT":
            if bus.next_station_idx is None or bus.route_pos is None: #*must have an active route
                return None
            if station_idx < bus.next_station_idx: #*must not have been passed by the bus
                return None
            eta = bus.remaining_ticks
            #*Sum ticks from next stop til requested station (if the latter is
            #*located after the former)
            if station_idx > bus.next_station_idx:
                eta += sum(route.travel_ticks[bus.next_station_idx:station_idx])
            return eta
        
        if bus.status == "DWELLING":
            if bus.route_pos is None: #*must have an active route
                return None
            if station_idx < bus.route_pos: #*must not have been passed by the bus
                return None
            if station_idx == bus.route_pos: #*at station
                return 0
            #*Apart from adding the ticks in between stations, add remaining
            #*dweel time
            eta = bus.dwell_remaining + sum(route.travel_ticks[bus.route_pos:station_idx])
            return eta
        return None

    def build_observation(self) -> np.ndarray:
        """
        Build the flattened observation vector.

        Returns
        -------
        np.ndarray
            Observation array.
        """
        #*1) Set window size for normalization
        t_max = int(round(20 * 60 / self.config.dt_sec))
        if t_max <= 0:
            raise ValueError("t_max computed as 0; dt_sec too large for normalization window.")
        obs: List[float] = []
        buses_by_route: Dict[RouteId, List[Bus]] = {}

        #*2) Compute normalized queue and normalized ETA and free capacity for
        #*each station in the route
        for route_id in self.route_order:
            route = self.routes[route_id]
            buses_on_route = [
                b for b in self.buses if b.route_id == route_id and b.status in ("IN_TRANSIT", "DWELLING")
            ]
            buses_by_route[route_id] = buses_on_route
            for station_idx, station_id in enumerate(route.stations):
                station = self.stations[station_id]
                q_norm = station.q_norm(route_id) #*normalized queue

                eta_vals = []
                for bus in buses_on_route:
                    eta = self._eta_to_station(bus, route, station_idx)
                    if eta is not None:
                        eta_vals.append(eta)
                if eta_vals: #*pick ETA and free cap from the closest bus
                    eta = min(eta_vals)
                    eta_norm = min(eta, t_max) / t_max
                    closest_bus = min(
                        buses_on_route,
                        key=lambda b: self._eta_to_station(b, route, station_idx) or 10**9,
                    )
                    free_cap = closest_bus.capacity - closest_bus.pax
                    cap_norm = min(max(free_cap / closest_bus.capacity, 0.0), 1.0)
                else: #*if no buses on this route, pick worst values
                    eta_norm = 1.0
                    cap_norm = 0.0

                obs.extend([q_norm, eta_norm, cap_norm])

        #*3) Also for each route, compute normalized amount of buses in
        #*service, and mean gap and coefficient of variation between buses
        for route_id in self.route_order:
            buses_on_route = buses_by_route.get(route_id, [])
            in_service = len(buses_on_route)
            in_service_norm = in_service / max(self.config.fleet_size, 1)
            in_service_norm = min(in_service_norm, 1.0)

            gaps = self.headways[route_id]
            if gaps:
                mean_gap = float(np.mean(gaps))
                std_gap = float(np.std(gaps))
                cv_gap = std_gap / mean_gap if mean_gap > 0 else 0.0
            else:
                mean_gap = 0.0
                cv_gap = 0.0

            mean_gap_norm = min(mean_gap, t_max) / t_max if t_max > 0 else 0.0
            cv_gap = min(cv_gap, self.config.cv_max)
            cv_gap_norm = cv_gap / self.config.cv_max if self.config.cv_max > 0 else 0.0
            obs.extend([in_service_norm, mean_gap_norm, cv_gap_norm])

        #*4) For each terminal, compute normalized ready pool
        for terminal_id in self.terminal_order:
            terminal = self.terminals[terminal_id]
            pool_norm = len(terminal.ready_pool) / max(terminal.capacity, 1)
            pool_norm = min(pool_norm, 1.0)
            obs.append(pool_norm)

        #*5) Update time as sine and cosine if enabled
        if self.config.enable_time_features:
            horizon_sec = self.config.horizon_ticks * self.config.dt_sec
            if horizon_sec <= 0:
                obs.extend([0.0, 0.0])
            else:
                angle = 2 * np.pi * (self.time_sec % horizon_sec) / horizon_sec
                obs.extend([float(np.sin(angle)), float(np.cos(angle))])


        return np.asarray(obs, dtype=np.float32)

    def observation_dim(self) -> int:
        """
        Return the observation vector size.

        Returns
        -------
        int
            Observation dimension.
        """
        dim = 0
        for route in self.routes.values():
            dim += len(route.stations) * 3 #*normalized queue, eta and free cap
        dim += len(self.terminals) #*normalized ready pool
        dim += len(self.routes) * 3 #*normalized frac of buses in service, and
        #*mean and cv gap between buses of the same route
        if self.config.enable_time_features:
            dim += 2 #*time as sine and cosine values
        return dim

    def reward(self, metrics: Dict[str, int]) -> float:
        """
        Compute reward from per-tick metrics and queues.

        Weights:
        - B: boarding reward (positive).
        - Q: queue penalty (negative).
        - D: denied boarding penalty (negative).
        - U: dispatch cost (negative).
        References:
        - b_ref: boarding normalized by
        `reward_ref_boarding_bus_multiples * bus_capacity`.
        - q_ref: total queue normalized by
        `reward_ref_queue_fraction * q_max_total`.
        - d_ref: denied normalized by
        `reward_ref_denied_bus_multiples * bus_capacity`.
        - u_ref: dispatches normalized by
        `reward_ref_dispatch_count`.

        Parameters
        ----------
        metrics : Dict[str, int]
            Metrics returned from tick.

        Returns
        -------
        float
            Reward value.
        """
        total_queue = sum(station.total_queue() for station in self.stations.values())
        #*Values for normalization of:
        b_ref = self.config.reward_ref_boarding_bus_multiples * self.config.bus_capacity #*users boarded (def. ~3 busloads)
        q_ref = self.q_max_total * self.config.reward_ref_queue_fraction #*users waiting (def. ~1/4 of the max in the system)
        d_ref = self.config.reward_ref_denied_bus_multiples * self.config.bus_capacity #*users denied boarding (def. ~1 busload)
        u_ref = self.config.reward_ref_dispatch_count #*buses dispatched (def. 5)

        w_b = self.config.reward_weights.get("B", 1.0) #*boarding reward
        w_q = self.config.reward_weights.get("Q", 0.6) #*queue penalty
        w_d = self.config.reward_weights.get("D", 0.8) #*denied boarding penalty
        w_u = self.config.reward_weights.get("U", 0.05) #*dispatch cost

        reward = 0.0
        reward += w_b * (metrics["boarded"] / max(b_ref, 1))
        reward -= w_q * (total_queue / max(q_ref, 1))
        reward -= w_d * (metrics["denied"] / max(d_ref, 1))
        reward -= w_u * (metrics["dispatches"] / max(u_ref, 1))

        if metrics["invalid_actions"] > 0:
            reward -= self.config.invalid_action_penalty * metrics["invalid_actions"]
        return reward
