import random
import collections
import pandas as pd
import math

"""
 Assumes the censor owns 100% of the accounts acting as the coupon collector
 Batch the distribution in groups of k, distribute in non-overlapping batches
"""
# print results
f = open("analysis/results_10_to_100_single_window_no_repeat.csv","w+")
flb = open("analysis/results_10_to_100_single_window_no_repeat_lb.csv","w+")

for run in range(10,100):
    trials = 1000
    n = run
    #print(n)
    seed = 43 # for reproducibility
    window_size = int(n/4) # set to n for no batching
    # create headers
    headers = []
    for i in range(1,n+1):
        headers.append("p%d" % i)
    print(headers)
    headers = ",".join(str(x) for x in headers)

    flb.write("%s,%s,%s,%s\r\n" % ("n","num_tries","optimal_load",headers))

    #print("window size = %d" %window_size)
    window_increment = window_size # to simpify, there are *no overlapping batches*
    window_repeat = 1 # higher repeats is making coupons "rarer"
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
        miss = 0
        num_tries = 0

        while (len(known_proxies) < n):

            random_interval_1 = random.randint(0, window_size-1)
            random_index_1 = (random_interval_1 + i) % n
            random_proxy_1_load = df.at[random_index_1,'load']
            #print("random interval 1 = %d random index 1 = %d proxy load = %d" % (random_interval_1, random_index_1, random_proxy_1_load))

            random_interval_2 = random.randint(0, window_size-1)
            random_index_2 = (random_interval_2 + i) % n
            random_proxy_2_load = df.at[random_index_2,'load']
            #print("random interval 2 = %d random index 2 = %d proxy load 2 = %d" % (random_interval_2, random_index_2, random_proxy_2_load))

            chosen_proxy_index = random_index_1

            # Assign the proxy with the highest load to unbalance them
            if (random_proxy_1_load < random_proxy_2_load):
                chosen_proxy_index = random_index_2

            if (chosen_proxy_index not in known_proxies):
                known_proxies.append(chosen_proxy_index)

            df.at[chosen_proxy_index,'load'] = df.at[chosen_proxy_index,'load'] + 1

            for window in range(0, window_size):
                index = (window + i) % n
                df.at[index,'num_in_draw'] = df.at[index,'num_in_draw'] + 1

            #print("i=%d j=%d rand_index=%d " % (i,j,chosen_proxy_index))
            current_repeat = current_repeat + 1
            if (current_repeat > window_repeat):
                #print("repeat = %d " % current_repeat)
                i = (i + window_increment) % n
                j = (j + window_increment) % n

                current_repeat = 1

            num_tries = num_tries + 1

        print(df)
        # Calculate the "optimal load"
        optimal_load = num_tries/n
        print("optimal_load = %d / %d = %d" %(num_tries, n, optimal_load) )
        # Sum up the optimal load deviation with a number for all above and another for all below
        # so that min bins don't cancel out max bins
        #min_optimal = (df.load < optimal_load).sum()
        sorted_loads = df.load.values.sort()
        loads = ",".join(str(x) for x in df.load.values)
        print(loads)

        flb.write("%d,%d,%d,%s\r\n" % (n,num_tries,optimal_load,loads))

        df_all = df_all.append(df, ignore_index=True)
    #print(df_all)
    # group by trial to find the number of draws in each trial (the E[T])
    df_all_group = df_all.groupby('trial', as_index=False, sort=False)['load'].sum()
    #print(df_all_group.load.describe())
    mean_samples = df_all_group.load.mean()
    #print("*****************     Sample mean = %d n = %d *********************" % (mean_samples, n))
    #print(df_all)
    # The max load in each trial (not the max load over all trials)
    df_all_max = df_all.groupby('trial', as_index=False, sort=False)['load'].max()
    #print("maximum loads average")
    #print(df_all_max)
    # The min load in each trial (not the min load over all trials)
    #df_all_min = df_all.groupby('trial', as_index=False, sort=False)['load'].min()
    #print("# all min")
    #print(df_all_min) # note min will always be 1 because it is the last proxy that is discovered

    df_count_min = df_all.loc[df_all['load'] == 1]

    #print("count of singletons per trial")
    #print(df_count_min.groupby('trial', as_index=False, sort=False)['load'].sum())
    #df_all.groupby('trial', as_index=False, sort=False)['load'].sum()


    # nH_n Formula using Euler Mascheroni Constant
    H_n = (math.log(n) + 0.5772156649) + 1/(2*n)
    #print("H_n %f" % H_n)
    nH_n = n * H_n
    #print("Calculated mean nH_n = %f" % (nH_n))
    # ln n / ln ln n
    ur_max_load = math.log(n) / (math.log(math.log(n)))
    #print("Calculated max load for uniform random %f where m=n" % ur_max_load)
    # ln ln n / ln 2
    pod_max_load = math.log(math.log(n))/math.log(2)
    #print("Calculated max load for power of 2 choice %f where m=n" % pod_max_load)
    # O(ln ln n) + m/n
    pod_max_load_m_sgr_n = math.log(math.log(n)) + mean_samples/n
    #print("Calculated max load for power of 2 choice %f where m >> n" % pod_max_load_m_sgr_n)

    max = df_all_group.load.max()
    min = df_all_group.load.min()
    std = df_all_group.load.std()
    #print("%d,%d,%d,%d,%d,%d\r\n" % (n,trials,mean_samples,max,min,std))
    f.write("%d,%d,%d,%d,%d,%d\r\n" % (n,trials,mean_samples,max,min,std))

f.flush()
f.close()
flb.flush()
flb.close()
