import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('.')
from core import util
from simulation import simulate_PoD

def collateral_damage_boxplot():
    """
     Track the total of enumerated proxies over time
    """
    print("________________________________Collateral Damage____________________________________\n")

    seed = util.SEED
    trial = 0
    df_all_pod = pd.DataFrame()

    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        seed = seed + 1
        client_arrival_rate = util.CLIENT_ARRIVAL_RATE

        # Client arrival rate sweep, create one graph per sweep
        for j in range(0, util.SWEEP):
            # Power of D Choices Analysis
            filename = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            df_pod = pd.read_csv(filename)
            df_pod = df_pod[(df_pod.action == 'ENUMERATE_PROXY')].round()
            df_pod = df_pod[['time']]
            # Each occurrence in the logs counts as 1 proxy enumeration
            df_pod['count'] = 1
            df_pod['trial'] = trial
            #df_pod = df_pod.groupby('time').agg(np.size)
            #print(type(df_pod))

            #print(" df pod")
            print(df_pod)
            df_all_pod = df_all_pod.append(df_pod, sort=True, ignore_index=True)

    print("all together now")
    print(df_all_pod)

    # Group each trial in a time series bin array of 10 ms each
    # TODO max time instead of hard coded value
    bin_array = np.linspace(0, 200, 21)
    df_grouped = df_all_pod.groupby(['time','trial']).agg(np.size)
    print(df_grouped)
    #bins = pd.cut(df_all_pod['time'], bin_array)
    #df_all_pod = df_all_pod.groupby(bins)["count"].agg([np.sum, np.mean, np.std])
    bins = pd.cut(df_grouped['time'], bin_array)
    df_grouped = df_grouped.groupby(bins)["count"].agg([np.sum, np.mean, np.std])

    print("grouped and all together now")
    print(df_grouped)

    #df_pod.groupby(bins)["count"].agg(np.sum)
    #df_all_pod = df_all_pod.groupby(bins)["count"].agg([np.sum, np.mean, np.std])
    # Create graph with all trials and experiments
    title="Number of proxies exposed over time in %d trials using %d proxies" % (util.NUM_TRIALS, util.NUM_PROXIES)
    plt.title(title)
    plt.xlabel("Binned event time (ms)")
    plt.ylabel("Number of Exposed Proxies")

    #plt.scatter(df_all_pod.cum_sum, df_all_pod.time, c="g", edgecolors="black", marker="o", label="Power of D Choices", alpha="0.7")
    #plt.legend(loc='upper left')

if __name__ == '__main__':
    collateral_damage_boxplot()
