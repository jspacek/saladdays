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
            df_all_pod = df_all_pod.append(df_pod, sort=True, ignore_index=True)

    # Group each entry by ms time and trial number
    bin_array = np.linspace(0, 200, 21)
    bins = pd.cut(df_all_pod['time'], bin_array)
    print(bins)
    df_all_pod = df_all_pod.groupby([bins])

    # Create graph with all trials and experiments
    title="Number of proxies exposed over time in %d trials using %d proxies" % (util.NUM_TRIALS, util.NUM_PROXIES)
    fig1, ax1 = plt.subplots()
    ax1.set_xlabel("Binned event time (10 ms)")
    ax1.set_ylabel("Number of Exposed Proxies")
    ax1.set_title(title)
    all = []
    # Select the maximum cumulative sum in each trial for each time slice
    for name, bin in df_all_pod:
        max_list = bin.groupby(['trial'], as_index=False, sort=False)['count'].max()
        max = max_list['count'].tolist()
        print(max)
        all.append(max)

    ax1.boxplot(all)
    plt.show()

if __name__ == '__main__':
    collateral_damage_boxplot()
