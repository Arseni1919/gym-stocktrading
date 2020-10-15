import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time
import pandas as pd

# -------------------------------------------- #
# INITIALIZATION
# -------------------------------------------- #
DATA_SOURCE = 'data/AAPL.csv'
# -------------------------------------------- #


class StockTrading(gym.Env):
    metadata = {'render.modes': ['human']}
    action_space = gym.spaces.Discrete(4)

    def __init__(self):
        self.db = self._prepare_data()
        self.start = 0
        self.action = 0

    def _prepare_data(self):
        df = pd.read_csv(DATA_SOURCE)
        df = df.sort_values('Date')
        adjust_ratio = 1
        df['Open'] = df['Open'] * adjust_ratio
        df['High'] = df['High'] * adjust_ratio
        df['Low'] = df['Low'] * adjust_ratio
        df['Close'] = df['Close'] * adjust_ratio

        return df

    def step(self, action):
        self.action = action
        observation = self.db.iloc[self.start]
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
        print(f'obs: {self.db.iloc[self.start]} action:{self.action}')

    def close(self):
        pass
