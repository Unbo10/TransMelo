from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from .route import Route
from .terminal_spec import TerminalSpec
from .types import RouteId, StationId, TerminalId


@dataclass
class BRTConfig:
    """

    Configuration for the BRT environment.

    Attributes
    ----------
    dt_sec : float
        Seconds per tick. Default is 10.0.
    horizon_ticks : int
        Episode length in ticks. Default is 6120 (17 hours with 10-second
        ticks).
    bus_capacity : int
        Capacity per bus. Default is 250.
    fleet_size : int
        Total number of buses in the fleet. Default is 20.
    dwell_ticks : int
        Legacy dwell time setting (kept for compatibility). Default is 2.
    terminal_capacity : int
        Default terminal capacity if needed. Default is 10.
    prep_time_ticks : int
        Default terminal prep time if needed. Default is 75.
    demand_mode : str
        "poisson" or "deterministic". Default is "deterministic".
    demand_rates : Dict[RouteId, Dict[StationId, float]]
        Mean arrivals per tick for each station and route. Default is empty.
    demand_by_route : Dict[StationId, Dict[RouteId, np.ndarray]]
        Time-varying arrivals per station and route. Default is empty.
    q_max_by_route : Dict[StationId, Dict[RouteId, int]]
        Queue normalization max per station and route. Default is empty.
    terminals : List[TerminalSpec]
        Terminal configuration records. Default is empty.
    routes : List[Route]
        Route definitions. Default is empty.
    terminal_routes : Dict[TerminalId, List[RouteId]]
        Allowed routes per terminal. Default is empty.
    route_endpoints : Dict[RouteId, List[StationId]]
        Allowed endpoint stations per route. Default is empty.
    terminal_transfer_times : Dict[TerminalId, Dict[TerminalId, int]]
        Transfer travel time between terminals, in ticks. Default is empty.
    headway_window : int
        Rolling window size for headway stats, e.g., since default is 5, to
        compute headway stats, only the five most recent services per route
        will be used to compute stats.
    rng_seed : Optional[int]
        RNG seed for reproducibility. Default is None.
    enable_time_features : bool
        Whether to include time features (time in cosine and sine) in
        observations. Default is True.
    cv_max : float
        Maximum coefficient of variation for headway normalization. Default is
        3.0.
    invalid_action_penalty : float
        Penalty per invalid action. Default is 0.1.
    default_boarding_rate : float
        Default boarding rate if not specified per station. Default is 1.0.
    default_alight_rate : float
        Default alight rate if not specified per station. Default is 0.3.
    default_station_hold_ticks : int
        Default station hold time in ticks. Default is 0.
    station_boarding_rates : Dict[StationId, float]
        Per-station boarding rate overrides. Default is empty.
    station_alight_rates : Dict[StationId, float]
        Per-station alight rate overrides. Default is empty.
    station_hold_times : Dict[StationId, int]
        Per-station base hold times in ticks. Default is empty.
    reward_weights : Dict[str, float]
        Reward component weights. Default is {"B": 1.0, "Q": 0.6, "D": 0.8,
        "U": 0.05}.
    reward_ref_boarding_bus_multiples : float
        Bus-load multiplier for boarding normalization. Default is 3.0.
    reward_ref_queue_fraction : float
        Fraction of total q_max used to normalize queues. Default is 0.25.
    reward_ref_denied_bus_multiples : float
        Bus-load multiplier for denied normalization. Default is 1.0.
    reward_ref_dispatch_count : float
        Dispatch count used to normalize dispatch cost. Default is 5.0.
    """
    dt_sec: float = 10.0
    horizon_ticks: int = 6120
    bus_capacity: int = 250
    fleet_size: int = 20
    dwell_ticks: int = 2
    terminal_capacity: int = 10
    prep_time_ticks: int = 75
    demand_mode: str = "deterministic"  #*poisson or deterministic
    demand_rates: Dict[RouteId, Dict[StationId, float]] = field(default_factory=dict)
    demand_by_route: Dict[StationId, Dict[RouteId, np.ndarray]] = field(default_factory=dict)
    q_max_by_route: Dict[StationId, Dict[RouteId, int]] = field(default_factory=dict)
    terminals: List[TerminalSpec] = field(default_factory=list)
    routes: List[Route] = field(default_factory=list)
    terminal_routes: Dict[TerminalId, List[RouteId]] = field(default_factory=dict)
    route_endpoints: Dict[RouteId, List[StationId]] = field(default_factory=dict)
    terminal_transfer_times: Dict[TerminalId, Dict[TerminalId, int]] = field(default_factory=dict)
    headway_window: int = 5
    rng_seed: Optional[int] = None
    enable_time_features: bool = True
    cv_max: float = 3.0
    invalid_action_penalty: float = 0.1

    #*Boarding/Alighting constants
    default_boarding_rate: float = 1.0
    default_alight_rate: float = 0.3
    default_station_hold_ticks: int = 0
    station_boarding_rates: Dict[StationId, float] = field(default_factory=dict)
    station_alight_rates: Dict[StationId, float] = field(default_factory=dict)
    station_hold_times: Dict[StationId, int] = field(default_factory=dict)

    #*Reward function weights
    reward_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "B": 1.0, #*boarding reward
            "Q": 0.6, #*queue penalty
            "D": 0.8, #*denied boarding penalty
            "U": 0.05, #*dispatch cost
        }
    )
    reward_ref_boarding_bus_multiples: float = 3.0
    reward_ref_queue_fraction: float = 0.25
    reward_ref_denied_bus_multiples: float = 1.0
    reward_ref_dispatch_count: float = 5.0

    #TODO: Update with real-life data
    @staticmethod
    def default() -> "BRTConfig":
        """Return a default toy configuration.

        Returns
        -------
        BRTConfig
            Default configuration object.
        """
        stations_b16 = ["EDO", "S1", "ALCA", "S2", "NORTE"]
        stations_b23 = ["EDO", "S1", "ALCA", "S3", "NORTE"]
        stations_k16 = list(reversed(stations_b16))
        stations_k23 = list(reversed(stations_b23))

        routes = [
            Route("B16", stations_b16, [2, 2, 2, 2], extra_dwell_ticks=1, end_terminal_id="T1"),
            Route("B23", stations_b23, [2, 2, 2, 2], extra_dwell_ticks=1, end_terminal_id="T1"),
            Route("K16", stations_k16, [2, 2, 2, 2], extra_dwell_ticks=1, end_terminal_id="T0"),
            Route("K23", stations_k23, [2, 2, 2, 2], extra_dwell_ticks=1, end_terminal_id="T0"),
        ]

        terminals = [
            TerminalSpec("T0", "EDO", capacity=6, prep_time_ticks=2),
            TerminalSpec("T1", "NORTE", capacity=6, prep_time_ticks=2),
            TerminalSpec("T2", "ALCA", capacity=4, prep_time_ticks=2),
        ]

        terminal_routes = {
            "T0": ["B16", "B23"],
            "T1": ["K16", "K23"],
            "T2": ["K16", "K23"],
        }

        route_endpoints = {
            "B16": ["ALCA", "NORTE"],
            "B23": ["ALCA", "NORTE"],
            "K16": ["ALCA", "EDO"],
            "K23": ["ALCA", "EDO"],
        }

        demand_rates: Dict[RouteId, Dict[StationId, float]] = {}
        for route in routes:
            demand_rates[route.route_id] = {s: 1.5 for s in route.stations}
            demand_rates[route.route_id][route.stations[0]] = 0.0
            demand_rates[route.route_id][route.stations[-1]] = 0.0

        return BRTConfig(
            demand_rates=demand_rates,
            terminals=terminals,
            routes=routes,
            terminal_routes=terminal_routes,
            route_endpoints=route_endpoints,
        )
