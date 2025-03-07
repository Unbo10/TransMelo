import gymnasium as gym

from src.utilities.data_getter.data_array import create_data_array
from src.utilities.data_structures.intArr import IntArr
from src.utilities.data_structures.objArr import ObjArr
from src.utilities.objects.bus import Bus
from src.utilities.data_structures.graph.weighted import Weighted as Graph

class Env:
    def __init__(self, graph: Graph, num_buses: IntArr, start_time: int, end_time: int, time_step: int):
        """
        Initialize the environment for the transportation problem.

        Parameters
        ----------
        graph : Graph
            The graph representing the transitway.
            Nodes are stations and edges are the time and distance betwee two
            of them.
        num_buses : IntArr
            Array containing the number of buses for each deployment site or
            host.
        max_time : int
            Maximum allowed time for the simulation to last (in minutes).
        """

        self.__graph: Graph = graph
        self.__num_buses: IntArr = num_buses
        self.__end_time: int = end_time
        self.__start_time: int = start_time
        self.__time_step: int = time_step
        self.reset()

    def reset(self):
        """
        Resets the environment to its initial state.
        """

        self.buses: ObjArr = ObjArr(self.__num_buses)
        for i in range(len(self.buses)):
            self.buses[i] = Bus(i) #!Capacity could be modified
        
        self.passenger_demand: ObjArr = create_data_array()
        return self.get_state()