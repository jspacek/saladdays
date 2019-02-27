import random
import collections
import pandas as pd
import math

"""
 Assume the censor owns 100% of the accounts acting as the coupon collector
"""

trials = 100
n = 120
seed = 42 # for reproducibility
window_size = 4
window_increment = 1#window_size # to simpify, there are no overlapping batches
window_repeat = 10 # higher repeats is making coupons "rarer"
# better results with lower window_increment and higher repeat (just makes batches used more frequently)
# with each guess repeat from the same set, the other coupons become rarer and rarer (and also lightly loaded)
proxy = collections.namedtuple('proxy', 'index load num_in_draw trial')
df_all = pd.DataFrame(columns=proxy._fields)

for current_trial in range(0,trials):
    proxies = [proxy(index=i,load=0,num_in_draw=0,trial=current_trial) for i in range(n)]
    df = pd.DataFrame(proxies, columns=proxy._fields)
    known_proxies = []
    seed = seed + 1
    random.seed(seed)
    i = 0
    j = 0 + window_size
    current_repeat = 1

    while (len(known_proxies) < n):

        random_interval = random.randint(0, window_size)
        random_index = (random_interval + i) % n
        #df = df.sort_values(by=['load'], ascending=False)
        #df = df.reset_index(drop=True)
        #print(df)
        random_proxy_victim = proxies[random_index]

        if (random_index not in known_proxies):
            known_proxies.append(random_index)

        df.at[random_index,'load'] = df.at[random_index,'load'] + 1
        #print("should have updated %d " % random_index)
        #print(df)
        for window in range(0, window_size):
            index = (window + i) % n
            df.at[index,'num_in_draw'] = df.at[index,'num_in_draw'] + 1

        #print("i=%d j=%d rand_index=%d " % (i,j,random_index))
        current_repeat = current_repeat + 1
        if (current_repeat > window_repeat):
            #print("repeat = %d " % current_repeat)
            i = (i + window_increment) % n
            j = (j + window_increment) % n
            current_repeat = 1

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
