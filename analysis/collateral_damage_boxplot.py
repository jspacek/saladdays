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
    df_all_pod = pd.DataFrame(columns=['time','count'])
    df_all_uni = pd.DataFrame(columns=['time','count'])
    df_all_sand = pd.DataFrame(columns=['time','count'])

    for i in range(0, 2):#util.NUM_TRIALS):
        trial = trial + 1
        seed = seed + 1
        client_arrival_rate = util.CLIENT_ARRIVAL_RATE

        # Client arrival rate sweep, create one graph per sweep
        for j in range(0, util.SWEEP):
            # Power of D Choices Analysis
            filename = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            #print(filename)
            df_pod = pd.read_csv(filename)
            # Filter file for relevant information
            df_pod = df_pod[['time','action']]
            df_pod = df_pod[(df_pod.action == 'ENUMERATE_PROXY')]
            df_pod = df_pod.round()
            print(df_pod)
            #df_pod = df_pod.groupby(df_pod['time']).count()
            #print(df_pod)
            # Group the number of proxies enumerated by time (not including misses)
            # Each occurrence in the logs counts as 1 proxy enumeration
            grouped = df_pod.groupby('time').agg(np.size)
            print(grouped)
            df_all_pod = df_all_pod.append(grouped)
            print(df_all_pod)

        # Group the entire set of trials by a time series bin
        large_grouped = df_all_pod.groupby('time').agg([np.size])
        #large_grouped = df_all_pod.groupby('time').agg([np.sum, np.mean, np.std])
        print(grouped.agg([np.sum, np.mean, np.std]))
        print(df_all_pod)

    # Create graph with all trials and experiments
    title="Collateral Damage: %d Trials sweep_%d_%d_%d" % (util.NUM_TRIALS, util.SWEEP, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
    plt.title(title)
    plt.xlabel("Event Time")
    plt.ylabel("Number of Honest Clients")
    #plt.scatter(df_all_pod.cum_sum, df_all_pod.time, c="g", edgecolors="black", marker="o", label="Power of D Choices", alpha="0.7")
    #plt.legend(loc='upper left')

if __name__ == '__main__':
    collateral_damage_boxplot()
