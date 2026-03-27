from __future__ import annotations

from typing import List

from .world import ActionCandidate, World


def always_dispatch(route_id: str, candidates: List[ActionCandidate]) -> int:
    """
    Pick the first dispatch candidate matching `route_id`, else HOLD (0).
    """
    for idx, cand in enumerate(candidates):
        if cand.kind == "DISPATCH" and cand.route_id == route_id:
            return idx
    return 0


def queue_greedy(world: World, candidates: List[ActionCandidate]) -> int:
    """
    Choose dispatch candidate with highest downstream queue pressure; else HOLD.
    """
    best_idx = 0
    best_pressure = -1.0
    for idx, cand in enumerate(candidates):
        if cand.kind != "DISPATCH" or cand.route_id is None:
            continue
        route = world.routes.get(cand.route_id)
        if route is None:
            continue
        pressure = 0.0
        for station_id in route.stations:
            station = world.stations[station_id]
            pressure += station.total_queue()
        if pressure > best_pressure:
            best_pressure = pressure
            best_idx = idx
    return best_idx
