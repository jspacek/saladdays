import random
import collections
import pandas as pd
import math

"""
 Assumes the censor owns 100% of the accounts acting as the coupon collector
"""

trials = 10
n = 16
seed = 43 # for reproducibility
proxy = collections.namedtuple('proxy', 'index load num_in_draw trial')
df_all = pd.DataFrame(columns=proxy._fields)

for current_trial in range(0,trials):
    proxies = [proxy(index=i,load=0,num_in_draw=0,trial=current_trial) for i in range(n)]
    df = pd.DataFrame(proxies, columns=proxy._fields)
    known_proxies = []
    seed = seed + 1
    random.seed(seed)

    while (len(known_proxies) < n):
        random_index = random.randint(0, n-1)
        print("rand_index=%d " % (random_index))

        random_proxy_victim = proxies[random_index]

        if (random_index not in known_proxies):
            known_proxies.append(random_index)

        df.at[random_index,'load'] = df.at[random_index,'load'] + 1


    df_all = df_all.append(df, ignore_index=True)

# group by trial to find the number of draws in each trial (the E[T])
df_all_group = df_all.groupby('trial', as_index=False, sort=False)['load'].sum()
print(df_all_group.load.describe())
mean_samples = df_all_group.load.mean()
print("*****************     Sample mean = %d *********************" % mean_samples)
# The max load in each trial (not the max load over all trials)
df_all_max = df_all.groupby('trial', as_index=False, sort=False)['load'].max()
print(df_all_max.load.mean())

# nH_n Formula using Euler Mascheroni Constant
nH_n = n * (math.log(n) + 0.5772156649) + 1/2
print("Calculated mean nH_n = %d" % (nH_n))
# ln n / ln ln n
ur_max_load = math.log(n) / (math.log(math.log(n)))
print("Calculated max load for uniform random %f" % ur_max_load)
# ln ln n / ln 2
pod_max_load = math.log(math.log(n))/math.log(2)
print("Calculated max load for power of 2 choice %f" % pod_max_load)
