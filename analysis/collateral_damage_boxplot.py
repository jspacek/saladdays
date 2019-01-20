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
            print(df_pod)
            df_pod = df_pod.groupby([df_pod.time], as_index=False, sort=False).agg(np.size)
            print(df_pod)

            df_pod['trial'] = trial
            df_pod['count'] = df_pod['count'].cumsum()
            print(df_pod)
            df_all_pod = df_all_pod.append(df_pod, sort=True, ignore_index=True)

    # Group each entry by ms time and trial number
    bin_array = np.linspace(0, 200, 21)
    #df_grouped = df_all_pod.groupby(['time','trial'], as_index=False, sort=False).agg(np.sum)
    #print("df grouped")
    #print(df_grouped)
    bins = pd.cut(df_all_pod['time'], bin_array)
    print(bins)
    df_all_pod = df_all_pod.groupby(bins)
    #["count"]# .agg([np.sum, np.mean, np.max, np.min, np.std])
    print(len(df_all_pod))

    for name, group in df_all_pod:
        print(name)
        print(group)

    # Create graph with all trials and experiments
    title="Number of proxies exposed over time in %d trials using %d proxies" % (util.NUM_TRIALS, util.NUM_PROXIES)
    plt.title(title)
    plt.xlabel("Binned event time (10 ms)")
    plt.ylabel("Number of Exposed Proxies")

    # fake up some data
    spread = np.random.rand(50) * 100
    center = np.ones(25) * 50
    flier_high = np.random.rand(50) * 100 + 100
    flier_low = np.random.rand(50) * -100
    #print(spread)
    #print(center)
    #print(flier_low)
    #print(flier_high)
    data = np.concatenate((spread, center, flier_high, flier_low))
    fig1, ax1 = plt.subplots()
    ax1.set_title('Basic Plot')
    ax1.boxplot(data)
    #plt.show()
    #plt.scatter(df_all_pod.cum_sum, df_all_pod.time, c="g", edgecolors="black", marker="o", label="Power of D Choices", alpha="0.7")
    #plt.legend(loc='upper left')

if __name__ == '__main__':
    collateral_damage_boxplot()
