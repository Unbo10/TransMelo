import torch
import torch.optim as optim
import torch.nn.functional as F
from optimization.ppo.network import ActorCritic
from config import Config

class PPOAgent:
    def __init__(self, state_dim, action_dim):
        self.model = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam(self.model.parameters(), lr=Config.LR)

    def get_action(self, state):
        state = torch.tensor(state, dtype=torch.float32)
        action_probs, value = self.model(state)
        dist = torch.distributions.Categorical(action_probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action), value

    def update(self, memory):
        states, actions, rewards, values, log_probs, dones = memory.get_tensors()

        # Compute advantages
        next_values = torch.cat((values[1:], torch.tensor([0])))
        deltas = rewards + Config.GAMMA * next_values * (1 - dones) - values
        advantages = deltas.clone()
        for t in reversed(range(len(deltas) - 1)):
            advantages[t] += Config.GAMMA * Config.LAMBDA * advantages[t + 1] * (1 - dones[t])

        # Compute returns
        returns = advantages + values

        # PPO policy update
        for _ in range(Config.EPOCHS):
            new_action_probs, new_values = self.model(states)
            dist = torch.distributions.Categorical(new_action_probs)
            new_log_probs = dist.log_prob(actions)

            ratio = torch.exp(new_log_probs - log_probs)
            clipped_ratio = torch.clamp(ratio, 1 - Config.EPSILON, 1 + Config.EPSILON)
            policy_loss = -torch.min(ratio * advantages, clipped_ratio * advantages).mean()

            value_loss = F.mse_loss(new_values.squeeze(), returns)
            loss = policy_loss + 0.5 * value_loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
