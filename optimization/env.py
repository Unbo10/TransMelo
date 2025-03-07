import gymnasium as gym
import numpy as np
from gymnasium import spaces

from src.utilities.data_getter.clean_data_array import clean_data_arr
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_structures.dictionary import Dictionary
from src.utilities.data_structures.graph.system_graph import SystemGraph
from src.utilities.objects.bus import Bus
from src.utilities.objects.route import Route
from src.utilities.objects.route_list import joint
from src.utilities.objects.station import Station


class TransMeloEnv(gym.Env):
    def __init__(self, stations: ObjArr, initial_buses: ObjArr, passenger_flow: Dictionary, u_turn_stations: ObjArr):
        super(TransMeloEnv, self).__init__()

        self.graph: SystemGraph = SystemGraph()
        self.station_names: ObjArr = stations
        self.buses: ObjArr = initial_buses
        self.passenger_flow: Dictionary = passenger_flow
        self.u_turn_stations: ObjArr = u_turn_stations
        self.route_decision = Dictionary()
        self.deploy_decision = Dictionary()

        self.num_stations = len(self.station_names)
        self.num_buses = len(self.buses)
        self.available_buses = ObjArr(self.num_buses)

        #* Action space: (U-turn decision + Deployment decision)
        self.action_space = spaces.MultiDiscrete([2, self.num_stations])

        #* Observation space: Buses' locations, passenger flow, and availability
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.num_stations * 2 + self.num_buses,), dtype=np.float32)

    def reset(self):
        """Resets the environment at the start of an episode."""
        for bus in self.buses:
            bus.location = None
            bus.number_of_passangers = 0

        self.available_buses = ObjArr(self.num_buses)
        return self.get_state()

    def get_state(self):
        """Encodes the current environment state as a numerical vector."""
        state = np.zeros(self.num_stations * 2 + self.num_buses, dtype=np.float32)

        #* Add passenger flow (entries and exits at each station)
        for i, station in enumerate(self.station_names):
            flow = self.passenger_flow.get(station, (0, 0))  # Default to (0,0) if no data
            state[2 * i] = flow[0]  # Entries
            state[2 * i + 1] = flow[1]  # Exits

        #* Add bus locations
        for i, bus in enumerate(self.buses):
            state[self.num_stations * 2 + i] = 1 if bus.location else 0

        return state

    def update_passenger_demand(self):
        """
        Simulates passengers entering and exiting buses at each station.
        """
        for bus in self.buses:
            if bus.location is not None:
                entering, exiting = self.passenger_flow.get(bus.location, (0, 0))
                bus.number_of_passangers = max(0, min(bus.capacity, 
                    bus.number_of_passangers + entering - exiting))

    def move_buses(self):
        """
        Updates bus locations based on predefined movement rules.
        """
        for bus in self.buses:
            if bus.location is not None:
                current_station = bus.location
                valid_moves = []

                # Iterate through all possible neighbors
                for neighbour, weight in self.graph.get_neighbours(current_station):
                    if neighbour in bus.route.station_names:
                        distance_needed = weight[0]  # Assuming weight[0] stores distance
                        if bus.distance_travelled >= distance_needed:
                            valid_moves.append((neighbour, distance_needed))

                # Select the closest valid move
                if valid_moves:
                    next_station, distance_travelled = min(valid_moves, key=lambda x: x[1])
                    bus.location = next_station
                    bus.distance_travelled = 0  # Reset since the bus moved
                else:
                    # If no valid moves were found, keep the bus in place
                    pass

            #* If the bus is at a U-turn station, allow switching routes
            if bus.location in self.u_turn_stations and self.route_decision.get(bus.id, False):  
                bus.route = "16" if bus.route == "23" else "23"

    def step(self, action):
        """
        Applies the agent's decision and updates the environment.
        """
        #* Apply action
        self.apply_action(action)

        #* Update passenger demand
        self.update_passenger_demand()

        #* Move buses
        self.move_buses()

        #* Construct the new observation
        new_observation = self.get_state()

        #* Compute reward
        reward = self.compute_reward()

        #* Check if episode is done
        done = self.check_termination()

        return new_observation, reward, done, {}

    def apply_action(self, action):
        """
        Applies the agent's action:
        - action[0]: U-turn decision (binary: 0 = No, 1 = Yes)
        - action[1]: Deployment decision (station index to deploy from)
        """
        u_turn_decision = action[0]  # 0 or 1
        deploy_station_index = action[1]  # Station index for deployment

        #*Handle U-turns
        for bus in self.buses:
            if bus.location in self.u_turn_stations:
                self.route_decision[bus.id] = bool(u_turn_decision)

        #*Handle Deployment
        if deploy_station_index < len(self.stations):  
            station = self.stations[deploy_station_index]
            if self.available_buses:
                bus = self.available_buses.pop()
                bus.location = station
                self.deployment_decision[bus.id] = deploy_station_index


    def render(self, mode="human"):
        """Displays the current state of the environment."""
        for bus in self.buses:
            print(f"Bus {bus.id}: Route {bus.route}, Location {bus.location}, Passengers {bus.number_of_passangers}/{bus.capacity}")
