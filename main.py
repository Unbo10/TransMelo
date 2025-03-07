#from src.utilities.data_getter import create_data_array
import gymnasium as gym
from optimization.ppo.trainer import train
from config import Config
import numpy as np
from src.web.page import *

if __name__ == "__main__":
    env = gym.make(Config.ENV_NAME)
    train(env)
