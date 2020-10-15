import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time


class StockTrading(gym.Env):
    metadata = {'render.modes': ['human']}
    action_space = gym.spaces.Discrete(4)

    def __init__(self):
        self.db = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.start = 0
        self.action = 0

    def step(self, action):
        self.action = action
        observation = self.db[self.start]
        reward = 1
        done = self.start == len(self.db) - 1
        info = ''
        time.sleep(1)
        if not done:
            self.start += 1
        return observation, reward, done, info

    def reset(self):
        self.start = 0

    def render(self, mode='human'):
        print(f'obs: {self.db[self.start]} action:{self.action}')

    def close(self):
        pass
