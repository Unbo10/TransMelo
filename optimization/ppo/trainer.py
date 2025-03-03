import torch
import numpy as np
from optimization.ppo.agent import PPOAgent
from optimization.ppo.memory import Memory
from config import Config
import pandas as pd
import os

np.bool8 = np.bool_
def train(env):
    state_dim = env.observation_space.shape[0]
    action_dim = env.action_space.n
    agent = PPOAgent(state_dim, action_dim)

    for episode in range(1000):
        memory = Memory()
        state = env.reset()[0]
        done = False
        total_reward = 0

        while not done:
            action, log_prob, value = agent.get_action(state)
            next_state, reward, done, _, _ = env.step(action)

            memory.add(state, action, reward, value.item(), log_prob.item(), done)
            state = next_state
            total_reward += reward

        agent.update(memory)

        if episode % 50 == 0:
            print(f"Episode {episode}: Reward = {total_reward}")
        log_reward(episode, total_reward)  # Guardar recompensa después de cada episodio




log_file = "ppo_training_log.csv"

def log_reward(episode, reward):
    data = {"Episode": [episode], "Reward": [reward]}
    df = pd.DataFrame(data)

    if os.path.exists(log_file):
        df.to_csv(log_file, mode="a", header=False, index=False)  # Añadir sin sobrescribir
    else:
        df.to_csv(log_file, index=False)

