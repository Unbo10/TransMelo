import torch
import numpy as np

class Memory:
    def __init__(self):
        self.states, self.actions, self.rewards = [], [], []
        self.values, self.log_probs, self.dones = [], [], []

    def add(self, state, action, reward, value, log_prob, done):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)

    def get_tensors(self):
        return (torch.tensor(np.array(self.states), dtype=torch.float32),
            torch.tensor(np.array(self.actions), dtype=torch.int64),
            torch.tensor(np.array(self.rewards), dtype=torch.float32),
            torch.tensor(np.array(self.values), dtype=torch.float32),
            torch.tensor(np.array(self.log_probs), dtype=torch.float32),
            torch.tensor(np.array(self.dones), dtype=torch.float32))

    def clear(self):
        self.states, self.actions, self.rewards = [], [], []
        self.values, self.log_probs, self.dones = [], [], []
