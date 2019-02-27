import random
import collections
import pandas as pd
import math

"""
 Assume the censor owns 100% of the accounts acting as the coupon collector
"""

trials = 300
n = 200
seed = 42 # for reproducibility
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
        #print("rand_index=%d " % (random_index))

        random_proxy_victim = proxies[random_index]

        if (random_index not in known_proxies):
            known_proxies.append(random_index)

        df.at[random_index,'load'] = df.at[random_index,'load'] + 1


    df_all = df_all.append(df, ignore_index=True)

#print(df_all)
# group by trial to find the number of draws in each trial (the E[T])
df_all = df_all.groupby('trial', as_index=False, sort=False)['load'].sum()
print(df_all)
mean_samples = df_all.load.mean()
print(mean_samples)

# todo group by trial print("real average # in draw %d " % df.num_in_draw.mean())
#print("Number of draws = %d " % draws )
# nH_n Formula using Euler Mascheroni Constant
nH_n = n * (math.log(n) + 0.5772156649) + 1/2
print(nH_n)

# max load appears to be really bad, worse than uni
