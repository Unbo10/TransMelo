from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Tuple

import numpy as np

from .bus import Bus
from .config import BRTConfig
from .route import Route
from .station import Station
from .terminal import Terminal
from .terminal_spec import TerminalSpec
from .types import RouteId, StationId, TerminalId


@dataclass
class ActionCandidate:
    """
    Atomic option available to the agent for a single decision event.
    """
    kind: str  # "HOLD", "DISPATCH", "TRANSFER"
    route_id: Optional[RouteId] = None
    end_station_id: Optional[StationId] = None
    end_idx: Optional[int] = None
    to_terminal_id: Optional[TerminalId] = None
    travel_ticks: Optional[int] = None


@dataclass
class DecisionEvent:
    """
    Represents a single decision for an available bus at a terminal.
    """
    event_type: str
    t_tick: int
    t_sec: float
    terminal_id: TerminalId
    bus_id: int
    candidates: List[ActionCandidate]


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
        self.event_queue: Deque[DecisionEvent] = deque()
        self.last_event_t: Optional[int] = None
        self.action_candidates_max = max(1, int(self.config.action_candidates_max))

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

    def _append_events_sorted(
        self,
        entries: List[Tuple[int, TerminalId]],
        event_t: Optional[int] = None,
        event_time_sec: Optional[float] = None,
    ) -> None:
        """
        Append decision events for ready buses, sorted by bus_id to keep order
        deterministic.
        """
        if not entries:
            return
        t_tick = self.t if event_t is None else event_t
        t_sec = self.time_sec if event_time_sec is None else event_time_sec
        for bus_id, terminal_id in sorted(entries, key=lambda e: e[0]):
            self.event_queue.append(
                DecisionEvent(
                    event_type="ASSIGN_BUS",
                    t_tick=t_tick,
                    t_sec=t_sec,
                    terminal_id=terminal_id,
                    bus_id=bus_id,
                    candidates=[],
                )
            )
        self.last_event_t = t_tick

    def _enqueue_available_buses_for_current_time(self) -> None:
        """
        If no pending events, enqueue ready buses for the current tick.
        """
        if self.event_queue:
            return
        if self.last_event_t is not None and self.last_event_t == self.t:
            return
        ready: List[Tuple[int, TerminalId]] = []
        for terminal_id in self.terminal_order:
            terminal = self.terminals[terminal_id]
            for bus_id in terminal.ready_pool:
                ready.append((bus_id, terminal_id))
        self._append_events_sorted(ready, event_t=self.t, event_time_sec=self.time_sec)

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
        self.event_queue = deque()
        self.last_event_t = None

        if not self.terminal_order:
            return

        ready_events: List[Tuple[int, TerminalId]] = []
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
            ready_events.append((bus.bus_id, terminal_id))

        self._append_events_sorted(ready_events, event_t=self.t, event_time_sec=self.time_sec)

    def _blank_metrics(self) -> Dict[str, int]:
        """
        Create an empty metrics dictionary for reward calculation.
        """
        return {
            "boarded": 0,
            "denied": 0,
            "dispatches": 0,
            "bus_transfers": 0,
            "invalid_actions": 0,
            "completed_routes": 0,
            "completed_by_route": {route_id: 0 for route_id in self.routes},
        }

    def blank_metrics(self) -> Dict[str, int]:
        """
        Public helper to create an empty metrics dictionary.
        """
        return self._blank_metrics()

    def peek_event(self) -> Optional[DecisionEvent]:
        """
        Return the current pending decision event without removing it.
        """
        if not self.event_queue:
            return None
        return self.event_queue[0]

    def pop_next_event(self) -> Optional[DecisionEvent]:
        """
        Pop the next pending decision event.
        """
        if not self.event_queue:
            return None
        return self.event_queue.popleft()

    def build_candidates(self, event: DecisionEvent) -> List[ActionCandidate]:
        """
        Build candidate list for a decision event, capped by action_candidates_max.
        """
        if event.event_type != "ASSIGN_BUS":
            event.candidates = [ActionCandidate(kind="HOLD")]
            return event.candidates

        terminal = self.terminals.get(event.terminal_id)
        bus = self.buses[event.bus_id] if 0 <= event.bus_id < len(self.buses) else None
        candidates: List[ActionCandidate] = [ActionCandidate(kind="HOLD")]
        if terminal is None or bus is None:
            event.candidates = candidates
            return event.candidates

        #*Only expose dispatch/transfer if the bus is actually ready at this terminal
        if bus.status == "READY_IN_POOL" and bus.terminal_id == terminal.terminal_id:
            for route_id, end_station_id, end_idx in self.dispatch_options.get(terminal.terminal_id, []):
                if len(candidates) >= self.action_candidates_max:
                    break
                candidates.append(
                    ActionCandidate(
                        kind="DISPATCH",
                        route_id=route_id,
                        end_station_id=end_station_id,
                        end_idx=end_idx,
                    )
                )
            if len(candidates) < self.action_candidates_max:
                transfer_opts = self.transfer_options.get(terminal.terminal_id, [])
                transfer_opts = transfer_opts[: self.config.transfer_candidates_top_k]
                for to_terminal_id, travel_ticks in transfer_opts:
                    if len(candidates) >= self.action_candidates_max:
                        break
                    candidates.append(
                        ActionCandidate(
                            kind="TRANSFER",
                            to_terminal_id=to_terminal_id,
                            travel_ticks=int(travel_ticks),
                        )
                    )

        event.candidates = candidates[: self.action_candidates_max]
        return event.candidates

    def _is_candidate_valid(self, event: DecisionEvent, candidate: ActionCandidate) -> bool:
        """
        Validate a candidate against the current world state.
        """
        if candidate.kind == "HOLD":
            return True
        bus = self.buses[event.bus_id] if 0 <= event.bus_id < len(self.buses) else None
        terminal = self.terminals.get(event.terminal_id)
        if bus is None or terminal is None:
            return False
        if bus.status != "READY_IN_POOL" or bus.terminal_id != terminal.terminal_id:
            return False
        if bus.bus_id not in terminal.ready_pool:
            return False

        if candidate.kind == "DISPATCH":
            if (
                candidate.route_id is None
                or candidate.end_station_id is None
                or candidate.end_idx is None
            ):
                return False
            if candidate.route_id not in self.config.terminal_routes.get(terminal.terminal_id, []):
                return False
            route = self.routes.get(candidate.route_id)
            if route is None:
                return False
            start_idx = route.station_index(terminal.station_id)
            if start_idx is None or start_idx >= len(route.stations) - 1:
                return False
            if candidate.end_idx <= start_idx:
                return False
            if candidate.end_station_id != route.stations[candidate.end_idx]:
                return False
            return True

        if candidate.kind == "TRANSFER":
            if candidate.to_terminal_id is None:
                return False
            to_terminal = self.terminals.get(candidate.to_terminal_id)
            if to_terminal is None:
                return False
            if (len(to_terminal.ready_pool) + len(to_terminal.prep_pool)) >= to_terminal.pool_capacity:
                return False
            return True
        return False

    def candidate_mask(self, event: DecisionEvent) -> np.ndarray:
        """
        Return boolean mask for a specific event's candidate list.
        """
        candidates = event.candidates or self.build_candidates(event)
        mask = np.zeros(self.action_candidates_max, dtype=bool)
        for idx, cand in enumerate(candidates):
            if idx >= self.action_candidates_max:
                break
            mask[idx] = self._is_candidate_valid(event, cand)
        return mask

    def _dispatch_bus(
        self,
        terminal_id: TerminalId,
        bus_id: int,
        route_id: RouteId,
        end_station_id: StationId,
        end_idx: int,
    ) -> bool:
        """
        Dispatch a specific ready bus from a terminal onto a route.
        """
        terminal = self.terminals.get(terminal_id)
        if terminal is None:
            return False
        if bus_id not in terminal.ready_pool:
            return False

        if route_id not in self.config.terminal_routes.get(terminal_id, []):
            return False
        route = self.routes.get(route_id)
        if route is None:
            return False
        start_idx = route.station_index(terminal.station_id)
        if start_idx is None or start_idx >= len(route.stations) - 1:
            return False
        if end_station_id != route.stations[end_idx]:
            return False
        if end_idx <= start_idx:
            return False

        popped_bus_id = terminal.dispatch(route_id=route_id, bus_id=bus_id)
        if popped_bus_id is None:
            return False

        bus = self.buses[popped_bus_id]
        bus.route_id = route_id
        bus.status = "IN_TRANSIT"
        bus.terminal_id = None
        bus.route_pos = start_idx
        bus.next_station_idx = start_idx + 1
        self.bus_end_idx[bus.bus_id] = end_idx
        bus.remaining_ticks = route.travel_ticks[start_idx]
        bus.dwell_remaining = 0

        last_dep = self.last_departure.get(route_id)
        if last_dep is not None:
            gap = self.t - last_dep
            self.headways[route_id].append(gap)
            if len(self.headways[route_id]) > self.config.headway_window:
                self.headways[route_id] = self.headways[route_id][-self.config.headway_window :]
        self.last_departure[route_id] = self.t
        return True

    def _transfer_bus(self, from_terminal_id: TerminalId, bus_id: int, to_terminal_id: TerminalId, travel_ticks: int) -> bool:
        """
        Move a ready bus into the transfer queue towards another terminal.
        """
        from_terminal = self.terminals.get(from_terminal_id)
        to_terminal = self.terminals.get(to_terminal_id)
        if from_terminal is None or to_terminal is None:
            return False
        if bus_id not in from_terminal.ready_pool:
            return False
        if (len(to_terminal.ready_pool) + len(to_terminal.prep_pool)) >= to_terminal.pool_capacity:
            return False
        popped_bus_id = from_terminal.dispatch(bus_id=bus_id)
        if popped_bus_id is None:
            return False
        self.transfer_queue.append((popped_bus_id, from_terminal_id, to_terminal_id, int(travel_ticks)))
        bus = self.buses[popped_bus_id]
        bus.status = "IN_TRANSFER"
        bus.terminal_id = None
        bus.route_id = None
        bus.route_pos = None
        bus.next_station_idx = None
        bus.remaining_ticks = 0
        bus.dwell_remaining = 0
        bus.pax = 0
        self.bus_end_idx[bus.bus_id] = None
        return True

    def apply_candidate(self, event: DecisionEvent, candidate: ActionCandidate) -> Dict[str, int]:
        """
        Apply a candidate action for a decision event and return resulting metrics.
        """
        metrics = self._blank_metrics()
        if candidate.kind == "HOLD":
            return metrics
        if not self._is_candidate_valid(event, candidate):
            metrics["invalid_actions"] += 1
            return metrics

        if candidate.kind == "DISPATCH":
            assert candidate.route_id is not None
            assert candidate.end_station_id is not None
            assert candidate.end_idx is not None
            accepted = self._dispatch_bus(
                terminal_id=event.terminal_id,
                bus_id=event.bus_id,
                route_id=candidate.route_id,
                end_station_id=candidate.end_station_id,
                end_idx=candidate.end_idx,
            )
            if accepted:
                metrics["dispatches"] += 1
            else:
                metrics["invalid_actions"] += 1
            return metrics

        if candidate.kind == "TRANSFER":
            assert candidate.to_terminal_id is not None
            travel_ticks = int(candidate.travel_ticks or 0)
            if travel_ticks < 0:
                metrics["invalid_actions"] += 1
                return metrics
            accepted = self._transfer_bus(
                from_terminal_id=event.terminal_id,
                bus_id=event.bus_id,
                to_terminal_id=candidate.to_terminal_id,
                travel_ticks=travel_ticks,
            )
            if accepted:
                metrics["bus_transfers"] += 1
            else:
                metrics["invalid_actions"] += 1
            return metrics

        metrics["invalid_actions"] += 1
        return metrics

    def advance_until_event(self) -> Tuple[float, bool]:
        """
        Advance simulation in internal ticks until an event is available or
        horizon reached.
        """
        reward_accum = 0.0
        truncated = self.t >= self.config.horizon_ticks

        self._enqueue_available_buses_for_current_time()
        if self.event_queue or truncated: #*action required or reached horizon
            return reward_accum, truncated

        while not self.event_queue and not truncated:
            metrics = self._advance_one_tick()
            reward_accum += self.reward(metrics)
            truncated = self.t >= self.config.horizon_ticks
            if truncated:
                break
            self._enqueue_available_buses_for_current_time()
            if self.event_queue:
                break
        return reward_accum, truncated

    def _advance_one_tick(self) -> Dict[str, int]:
        """
        Advance the world by a single tick (time step) without external actions.
        """
        metrics = self._blank_metrics()

        #*1) Update demand at each station
        for station in self.stations.values():
            new_demand = station.new_demand_at(self.t, self.rng)
            station.add_demand(new_demand)

        #*2) Move buses in transit towards next stop
        newly_arrived: set[int] = set()
        for bus in self.buses:
            if bus.status != "IN_TRANSIT" or bus.route_id is None:
                continue
            bus.remaining_ticks -= 1
            if bus.remaining_ticks > 0:
                continue
            #*Set bus to dwelling if it reached its next stop (no ticks remaining)
            route = self.routes[bus.route_id]
            bus.status = "DWELLING"
            bus.route_pos = bus.next_station_idx
            bus.next_station_idx = None
            station_id = route.stations[bus.route_pos]
            station = self.stations[station_id]
            bus.dwell_remaining = route.extra_dwell_ticks + station.dwell_ticks
            newly_arrived.add(bus.bus_id)

        #*3) Handle dwell: alight/board and route completion
        new_ready_events: List[Tuple[int, TerminalId]] = []
        for bus in self.buses:
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
                terminal = self.terminals[terminal_id]
                accepted = terminal.accept_bus(bus.bus_id)
                if not accepted:
                    raise RuntimeError(f"Terminal '{terminal_id}' is full; bus '{bus.bus_id}' cannot alight.")
                #*Reset bus info
                bus.status = "IN_TERMINAL_PREP"
                bus.terminal_id = terminal_id
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

        #*4) Update (bus) transfer queue
        idx = 0
        while idx < len(self.transfer_queue):
            bus_id, from_terminal_id, to_terminal_id, remaining_ticks = self.transfer_queue[idx]
            remaining_ticks -= 1
            if remaining_ticks == 0:
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
                else: #*if bus is rejected, leaves it in queue to retry next tick
                    self.transfer_queue[idx] = (bus_id, from_terminal_id, to_terminal_id, 1)
                    idx += 1
            else: #*just subtracted a remaining tick
                self.transfer_queue[idx] = (bus_id, from_terminal_id, to_terminal_id, remaining_ticks)
                idx += 1

        #*5) Tick prep pools and capture newly ready buses
        for terminal in self.terminals.values():
            ready_now = terminal.tick_prep()
            if ready_now:
                new_ready_events.extend((bus_id, terminal.terminal_id) for bus_id in ready_now)
            for bus_id in terminal.ready_pool:
                self.buses[bus_id].status = "READY_IN_POOL"
                self.buses[bus_id].terminal_id = terminal.terminal_id

        #*6) Advance time and enqueue events for buses that just became ready
        self.t += 1
        self.time_sec += self.config.dt_sec
        self._append_events_sorted(new_ready_events, event_t=self.t, event_time_sec=self.time_sec)
        return metrics

    def step_tick(self, action: Optional[np.ndarray] = None) -> Dict[str, int]:
        """
        Compatibility wrapper that advances one tick ignoring the action.
        """
        return self._advance_one_tick()

    def tick(self, action: Optional[np.ndarray] = None) -> Dict[str, int]:
        """
        Compatibility wrapper that advances one tick ignoring the action.
        """
        return self._advance_one_tick()

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

    def reward(self, metrics: Dict[str, int], include_queue: bool = True) -> float:
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
        include_queue : bool, optional
            Whether to include queue penalty (set False for instantaneous
            decision rewards without time advance).

        Returns
        -------
        float
            Reward value.
        """
        total_queue = sum(station.total_queue() for station in self.stations.values()) if include_queue else 0.0
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
