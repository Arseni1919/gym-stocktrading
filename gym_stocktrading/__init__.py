from gym.envs.registration import register

register(
    id='stocktrading-v0',
    entry_point='gym_stocktrading.envs:StockTrading',
)

# register(
#     id='foo-extrahard-v0',
#     entry_point='gym_foo.envs:FooExtraHardEnv',
# )
