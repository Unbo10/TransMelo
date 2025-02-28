import gymnasium as gym

class Env:
    def __init__(self):
        self.__graph: Graph = Graph()
        
        #* Three possible actions the agent can execute
        self.__action_space = gym.spaces.Discrete(3)

        #* 