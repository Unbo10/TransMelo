"""
ActorCritic Network Module for PPO Implementation

This module defines the neural network architecture used in a Proximal Policy 
Optimization (PPO) reinforcement learning algorithm. It implements an
Actor-Critic architecture where:

- The Actor network outputs action probabilities given a state
- The Critic network estimates the value function of a state

The networks share the same input (state representation) and underlying
structure (two hidden layers and ReLU activations) but have separate parameters
and output different quantities.

Often, the two networks are implemented separately, but together, they can
overcome some of the difficulties they have independently.

Classes:
    ActorCritic: A PyTorch module implementing both actor and critic networks
"""

import torch
import torch.nn as nn

class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(ActorCritic, self).__init__()

        self.actor = nn.Sequential(
            nn.Linear(state_dim, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, action_dim), nn.Softmax(dim=-1)
        )

        self.critic = nn.Sequential(
            nn.Linear(state_dim, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, state):
        action_probs = self.actor(state)
        value = self.critic(state)
        return action_probs, value
