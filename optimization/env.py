import gymnasium as gym
import numpy as np
from gymnasium import spaces
from stable_baselines3 import PPO

from src.utilities.data_getter.clean_data_array import clean_data_arr
from src.utilities.data_structures.lList import LList
from src.utilities.data_structures.dictionary import Dictionary
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.data_structures.graph.system_graph import SystemGraph
from src.utilities.objects.bus import Bus
from src.utilities.objects.route import Route
from src.utilities.objects.route_list import joint, r16, r23
from src.utilities.objects.station import Station


class TransMeloEnv(gym.Env):
    def __init__(
        self,
        station_names=None,
        station_list=None,
        initial_buses=None,
        passenger_flow=None,
        u_turn_stations=None,
        max_time=60
        ):
        super(TransMeloEnv, self).__init__()
        if station_names is None:
            station_names = joint().station_names
        if station_list is None:
            stations = ObjArr(22)
            joint_stations = joint()
            for i in range(len(stations)):
                stations[i] = Station(name=joint_stations.station_names[i])
            station_list = stations
        buses = LList()
        for i in range(10):
            buses.append(Bus(str(i)))
        initial_buses = buses
        if passenger_flow is None:
            passenger_flow = clean_data_arr()
        if u_turn_stations is None:
            u_turn = ObjArr(1)
            u_turn[0] = "Alcalá – Colegio S. Tomás Dominicos"
            u_turn_stations = u_turn

        self.graph: SystemGraph = SystemGraph()
        self.station_names: ObjArr = station_names
        self.stations: ObjArr = station_list
        self.buses: ObjArr = initial_buses
        self.passenger_flow: ObjArr = passenger_flow
        self.passenger_flow_dict: Dictionary = Dictionary(35)
        self.u_turn_stations: ObjArr = u_turn_stations
        self.route_decision = Dictionary(10)
        self.deploy_decision = Dictionary(10)
        self.max_time = max_time
        self.current_step: int = 0
        
        self.num_stations = len(self.station_names)
        self.num_buses = len(self.buses)
        self.available_buses = ObjArr(self.num_buses)

        #* Action space: (U-turn decision + Deployment decision)
        self.action_space = spaces.MultiDiscrete([2, self.num_stations])

        #* Observation space: Buses' locations, passenger flow, and availability
        self.observation_space = spaces.Box(low=0, high=1, shape=(self.num_stations * 2 + self.num_buses,), dtype=np.float32)
        self.process_passenger_data()


    def process_passenger_data(self):
        """
        Converts an ObjArr of linked lists into a dictionary mapping 
        station names to lists of (entries, exits) per minute.
        """
        for linked_list in self.passenger_flow:
            if linked_list is None or linked_list.head is None:
                continue
            
            current_node = linked_list.head
            data_list = LList()

            while current_node.next is not None: 
                entries, exits = current_node.value
                data_list.append((entries, exits))
                current_node = current_node.next

            station_name = current_node.value
            self.passenger_flow_dict.insert(station_name, data_list)


    def reset(self, seed=None, options=None, **kwargs):
        """Resets the environment at the start of an episode."""
        # Optional: set the random seed if provided
        if seed is not None:
            np.random.seed(seed)
            
        # Reset bus states
        for bus in self.buses:
            bus.location = None
            bus.number_of_passangers = 0

        self.available_buses = ObjArr(self.num_buses)
        
        # Initialize or reset current_time
        self.current_time = 0
        
        # Return both observation and info dict
        return self.get_state(), {}  # Return (observation, empty info dict)


    def get_state(self):
        """Encodes the current environment state as a numerical vector."""
        state: np.ndarray = np.zeros(self.num_stations * 2 + self.num_buses, dtype=np.float32)

        #* Add passenger flow (entries and exits at each station)
        for i, station in enumerate(self.station_names):
            try:
                flow = self.passenger_flow_dict.get(station)  # Default to (0,0) if no data
                state[2 * i] = flow[0]  # Entries
                state[2 * i + 1] = flow[1]  # Exits
            except KeyError:
                pass
                # print(station)
                # print(self.passenger_flow_dict)
            except ValueError:
                pass

        #* Add bus locations
        for i, bus in enumerate(self.buses):
            state[self.num_stations * 2 + i] = 1 if bus.location else 0

        return state


    def update_passenger_demand(self):
        """
        Simulates passengers entering and exiting buses at each station.
        - Updates the station's passenger count every minute.
        - Updates buses when they arrive at a station.
        - Uses an ObjArr of linked lists where each station stores (entries, exits) per minute.
        """
        # Track station passenger counts (keeps people waiting)
        for station in self.stations:
            passenger_data: LList = self.passenger_flow_dict[station.name]
            entering, exiting = passenger_data[self.current_time]
            print(entering, exiting)
            
            # Update station's waiting passengers
            station.current_passengers = max(0, station.current_passengers + entering - exiting)

        # Update buses picking up passengers
        for bus in self.buses:
            if bus.location is not None and bus.time_since_last_stop == 0:
                station_name = bus.location
                
                if station_name in self.passenger_flow_dict and bus.in_service:
                    # Bus picks up passengers
                    boarding = min(bus.capacity - bus.number_of_passangers, station.current_passengers)
                    
                    bus.number_of_passangers += boarding
                    station.current_passengers -= boarding  # Remove boarded passengers from station
        
        # Move to the next minute
        self.current_time += 1


    def move_buses(self):
        """
        Updates bus locations based on predefined movement rules.
        Allows for a U-turn decision and deployment of one or another route depending on where the bus is.
        """
        # print("Buses", self.buses)
        for bus in self.buses:
            if bus.location is not None:
                current_station = bus.location
                possible_moves = self.graph.get_neighbours(current_station)  # List of (neighbour, weight)
                valid_move_found = False
                
                # Iterate through neighbors to determine if the bus can move forward.
                for neighbour, weight in possible_moves:
                    # Only consider neighbors that are part of the bus's current route.
                    if neighbour in bus.route.station_names:
                        time_needed = weight[1]  # The required travel time to reach this neighbor.
                        
                        if bus.time_since_last_stop < time_needed:
                            # Bus is still en route; increment the timer.
                            bus.time_since_last_stop += 1
                            valid_move_found = True
                            break
                        elif bus.time_since_last_stop >= time_needed:
                            # The bus has reached the next station.
                            bus.location = neighbour
                            bus.time_since_last_stop = 0  # Reset travel timer upon arrival.
                            valid_move_found = True
                            break
                
                # If no valid move was found (i.e. bus is still waiting/traveling), increment the timer.
                if not valid_move_found:
                    bus.time_since_last_stop += 1

            # U-turn decision: if the bus is at a designated U-turn station and the decision for this bus is True,
            if bus.location in self.u_turn_stations and self.route_decision.get(bus.id) == True:
                bus.route = "K23"
            else:
                bus.route = "B16"
                bus.in_service = False

                # Optionally reset the travel timer after a U-turn.
                bus.time_since_last_stop = 0


    def apply_action(self, action: ObjArr):
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


    def compute_reward(self):
        reward = 0
        
        # Reward for passengers in transit
        total_passengers_in_buses = sum(bus.number_of_passangers for bus in self.buses if bus.location is not None)
        reward += total_passengers_in_buses * 0.5
        # print(f"Passengers in buses: {total_passengers_in_buses}, Reward: {total_passengers_in_buses * 0.5}")

        # Penalty for waiting passengers
        total_waiting_passengers = sum(station.current_passengers for station in self.stations)
        reward -= total_waiting_passengers * 0.2
        # print(f"Waiting passengers: {total_waiting_passengers}, Penalty: {total_waiting_passengers * 0.2}")

        # Penalty for unused capacity
        total_available_capacity = sum(bus.capacity - bus.number_of_passangers 
                                    for bus in self.buses 
                                    if bus.location is not None and bus.in_service)
        reward -= total_available_capacity * 0.1
        # print(f"Unused capacity: {total_available_capacity}, Penalty: {total_available_capacity * 0.1}")

        # Reward for serving high-demand stations
        for bus in self.buses:
            if bus.location is not None and bus.location in self.passenger_flow_dict:
                try:
                    station_demand = self.passenger_flow_dict.get(bus.location)[0]
                    if station_demand > 5:
                        reward += 3
                        print(f"High-demand station served: {bus.location}, Bonus: 3")
                except (TypeError, IndexError):
                    pass

        return reward




    def step(self, action: ObjArr):
        """
        Applies the agent's decision and updates the environment.
        """
        # Apply action
        self.apply_action(action)

        # Update passenger demand
        self.update_passenger_demand()

        # Move buses
        self.move_buses()

        self.current_step += 1

        # Construct the new observation
        new_observation = self.get_state()

        # Compute reward
        reward = self.compute_reward()

        # print(f"Step: {self.current_step}, Reward: {reward}")

        # Check if episode is done
        terminated = False
        truncated = False
        if self.current_time == self.max_time:
            terminated = True

        # In Gymnasium API, done is split into terminated and truncated
        # terminated = episode ended due to reaching a terminal state
        # truncated = episode ended due to external factors (like time limit)

        return new_observation, reward, terminated, truncated, {}


if __name__ == "__main__":
    buses: ObjArr = ObjArr(10)
    for i in range(len(buses)):
        buses[i] = Bus(i)
    u_turn: ObjArr = ObjArr(1)
    u_turn[0] = "Alcalá – Colegio S. Tomás Dominicos"
    stations: ObjArr = ObjArr(22)
    joint_stations: Route = joint()
    for i in range(len(stations)):
        stations[i] = Station(name=joint_stations.station_names[i])
    TransMeloEnv(station_names=joint().station_names, station_list=stations, initial_buses=buses, max_time=60, u_turn_stations=u_turn, passenger_flow=clean_data_arr())


gym.register(id="TransMelo-v0", entry_point=TransMeloEnv)

if __name__ == "__main__":

    env = gym.make("TransMelo-v0")

    # Initialize PPO model
    model = PPO("TransMelo-v0", env, verbose=1)

    # Train the agent
    model.learn(total_timesteps=5)

    # Save the trained model
    model.save("TransMelo-v0")
