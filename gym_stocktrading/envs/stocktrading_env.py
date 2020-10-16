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
INITIAL_ACCOUNT_BALANCE = 10000
MAX_STEPS_IN_ONE_BATCH = 20
MAX_ACCOUNT_BALANCE = 10 ** 7  # 2147483647 - max int32 number
MAX_NUM_SHARES = 10 ** 7
MAX_SHARE_PRICE = 1000


# -------------------------------------------- #


class StockTrading(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.db = self._prepare_data()
        self.len_of_db = len(self.db.loc[:, 'Close'].values)
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
        # print(df)

        return df

    def step(self, action):
        # Execute one time step within the environment
        self._take_action(action)

        self.current_step += 1
        delay_modifier = (self.current_step / MAX_STEPS_IN_ONE_BATCH)

        reward = self.balance * delay_modifier + self.current_step
        # reward = self.net_worth * delay_modifier + self.current_step

        done = self.net_worth <= 0 or self.current_step >= (self.len_of_db - LOOK_BACK_WINDOW_SIZE)

        obs = self._next_observation()
        info = {}

        return obs, reward, done, info

    def _take_action(self, action):
        current_change_in_price = self.db.loc[self.current_step + LOOK_BACK_WINDOW_SIZE, "Close"]
        current_price = self.db.loc[self.current_step + LOOK_BACK_WINDOW_SIZE, "Close"]

        action_type = action[0]
        amount = action[1]

        if action_type == 0:
            # Buy amount % of balance in shares
            total_possible = int(self.balance / current_price)
            shares_bought = int(total_possible * amount)
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price

            if shares_bought > 0:
                self.balance -= additional_cost
                self.cost_basis = (prev_cost + additional_cost) / (self.shares_held + shares_bought)
                self.shares_held += shares_bought

                self.trades.append({'step': self.current_step,
                                    'shares': shares_bought, 'total': additional_cost,
                                    'type': "buy"})
            # go_to_spend = self.balance * amount
            # self.balance -= go_to_spend
            # self.shares_held *= 1 + current_change_in_price
            # self.shares_held += go_to_spend

        elif action_type == 1:
            # Sell amount % of shares held
            shares_sold = int(self.shares_held * amount)

            if shares_sold > 0:
                self.balance += shares_sold * current_price
                self.shares_held -= shares_sold
                self.total_shares_sold += shares_sold
                self.total_sales_value += shares_sold * current_price
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
        self.current_step = random.randint(0, self.len_of_db - LOOK_BACK_WINDOW_SIZE)

        return self._next_observation()

    def _next_observation(self):
        obs = self.db.loc[self.current_step:self.current_step + LOOK_BACK_WINDOW_SIZE, 'Close'].to_numpy()
        # print(f'before: {obs}, {MAX_SHARE_PRICE}')
        obs /= MAX_SHARE_PRICE
        # print(f'after: {obs}')
        # Append additional data and scale each value to between 0-1
        # obs = obs.to_numpy()
        # print(f'before: {obs}')
        obs = np.append(obs, self.balance / MAX_ACCOUNT_BALANCE)
        obs = np.append(obs, self.max_net_worth / MAX_ACCOUNT_BALANCE)
        obs = np.append(obs, self.shares_held / MAX_NUM_SHARES)
        obs = np.append(obs, self.cost_basis / MAX_SHARE_PRICE)
        obs = np.append(obs, self.total_shares_sold / MAX_NUM_SHARES)
        obs = np.append(obs, self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE))
        # obs = np.append(obs,[
        #                 [self.balance / MAX_ACCOUNT_BALANCE],
        #                 [self.max_net_worth / MAX_ACCOUNT_BALANCE],
        #                 [self.shares_held / MAX_NUM_SHARES],
        #                 [self.cost_basis / MAX_SHARE_PRICE],
        #                 [self.total_shares_sold / MAX_NUM_SHARES],
        #                 [self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE)]])

        return obs

    def render(self, mode='human', close=False):
        # Render the environment to the screen
        profit = self.net_worth - INITIAL_ACCOUNT_BALANCE
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(f'Shares held: {self.shares_held} (Total sold: {self.total_shares_sold})')
        print(f'Avg cost for held shares: {self.cost_basis} Total sales value: {self.total_sales_value})')
        print(f'Net worth: {self.net_worth}(Max net worth: {self.max_net_worth})')
        print(f'Profit: {profit}')

    def close(self):
        pass
