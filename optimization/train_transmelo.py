import gymnasium as gym
from stable_baselines3 import PPO

# Ensure the environment is registered by importing it
from optimization.env import TransMeloEnv

def main():
    # Create the environment
    env = gym.make("TransMelo-v0")

    # Initialize the PPO model (first parameter is the policy type, not the env id)
    model = PPO("MlpPolicy", env, verbose=1)

    # Train the agent
    model.learn(total_timesteps=10000)

    # Save the model
    model.save("ppo_transmelo_model")

    # Optionally, run a test episode to check performance
    obs, info = env.reset()
    done = False
    while not done:
        action = env.action_space.sample()  # Replace with model.predict(obs) for a trained policy
        obs, reward, done, truncated, info = env.step(action)
        env.render()
        if done or truncated:
            break
    env.close()

if __name__ == "__main__":
    main()
