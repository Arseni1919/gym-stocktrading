import gym
from gym import error, spaces, utils
from gym.utils import seeding
import time
import pandas as pd
import numpy as np
import random

# -------------------------------------------- #
# INITIALIZATION
# -------------------------------------------- #
DATA_SOURCE = 'data/AAPL.csv'
MAX_JUMP_IN_STOCK_COST = 100
LOOK_BACK_WINDOW_SIZE = 20
MAX_ACCOUNT_BALANCE = 10 ^ 7
INITIAL_ACCOUNT_BALANCE = 10000
MAX_STEPS_IN_ONE_BATCH = 20

# -------------------------------------------- #


class StockTrading(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.db = self._prepare_data()
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)
        # 0 - Buy, 1 - Sell, 2 - Hold, (0, 1) - How much to buy / to sell
        self.action_space = spaces.Tuple(spaces=(spaces.Discrete(n=3),
                                                 spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)))
        # looking back
        self.observation_space = spaces.Box(low=0.0, high=MAX_JUMP_IN_STOCK_COST,
                                            shape=(LOOK_BACK_WINDOW_SIZE,), dtype=np.float32)

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
        # Execute one time step within the environment
        self._take_action(action)

        self.current_step += 1
        delay_modifier = (self.current_step / MAX_STEPS_IN_ONE_BATCH)

        reward = self.balance * delay_modifier + self.current_step
        # reward = self.net_worth * delay_modifier + self.current_step

        done = self.net_worth <= 0 or self.current_step >= (len(self.db.loc[:, 'Close'].values) - LOOK_BACK_WINDOW_SIZE)

        obs = self._next_observation()
        info = {}

        return obs, reward, done, info

    def _take_action(self, action):
        current_price = self.db.loc[self.current_step + LOOK_BACK_WINDOW_SIZE, "Close"]

        action_type = action[0]
        amount = action[1]

        if action_type == 0:
            # Buy amount % of balance in shares
            total_possible = int(self.balance / current_price)
            shares_bought = int(total_possible * amount)
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price

            self.balance -= additional_cost
            self.cost_basis = (
                                      prev_cost + additional_cost) / (self.shares_held + shares_bought + 1)
            self.shares_held += shares_bought

            if shares_bought > 0:
                self.trades.append({'step': self.current_step,
                                    'shares': shares_bought, 'total': additional_cost,
                                    'type': "buy"})

        elif action_type == 1:
            # Sell amount % of shares held
            shares_sold = int(self.shares_held * amount)
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price

            if shares_sold > 0:
                self.trades.append({'step': self.current_step,
                                    'shares': shares_sold, 'total': shares_sold * current_price,
                                    'type': "sell"})

        self.net_worth = self.balance + self.shares_held * current_price

        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth

        if self.shares_held == 0:
            self.cost_basis = 0

    def reset(self):
        # Reset the state of the environment to an initial state
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.net_worth = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
        self.shares_held = 0
        self.cost_basis = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.trades = []

        # Set the current step to a random point within the data frame
        # self.current_step = 0
        self.current_step = random.randint(0, len(self.db.loc[:, 'Close'].values) - LOOK_BACK_WINDOW_SIZE)

        return self._next_observation()

    def _next_observation(self):
        obs = self.db.iloc[self.current_step:self.current_step+LOOK_BACK_WINDOW_SIZE]
        return obs

    def render(self, mode='human'):
        # print(f'obs: {self.db.iloc[self.start]} action:{self.action}')
        pass

    def close(self):
        pass
