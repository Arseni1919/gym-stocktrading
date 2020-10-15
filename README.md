# Gym Env For Stock Trading

---

Created by Neural Trading (c)

Great thanks to:
 - [Adam King 1](https://towardsdatascience.com/creating-a-custom-openai-gym-environment-for-stock-trading-be532be3910e)

## Installation 

In order to run the environment you need to do the following:

1. Copy the repo to your computer.</il>
2. Go to the one directory above of the copied repo on your computer in the Terminal.
3. Click:

`
pip install -e gym-stocktrading
`
> That's it! You've installed the new gym-env on your computer.

## Sanity Check

In another project try to run the environment with this code:

```
import gym

env = gym.make('gym_stocktrading:stocktrading-v0')
ob = env.reset()
done = True

for i in range(100):
    while not done:
        action = env.action_space.sample()
        ob, reward, done, _ = env.step(action)
        env.render()
        if done:
            ob = env.reset()
            done = False

env.close()
```

---

 ***Enjoy!***
