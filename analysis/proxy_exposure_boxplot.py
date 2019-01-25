import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append('.')
from core import util
from simulation import simulate_PoD

def proxy_exposure_boxplot():
    """
     Track the total of enumerated proxies over time
    """
    print("________________________________Proxy Exposure____________________________________\n")

    seed = util.SEED
    trial = 0
    df_all_pod = pd.DataFrame()
    df_all_uni = pd.DataFrame()
    df_all_sandwich = pd.DataFrame()

    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        seed = seed + 1
        client_arrival_rate = util.CLIENT_ARRIVAL_RATE

        for j in range(0, util.SWEEP):
            # Power of D Choices Analysis
            filename = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            df_pod = pd.read_csv(filename)
            df_pod = df_pod[(df_pod.action == 'ENUMERATE_PROXY')].round()
            df_pod = df_pod[['time']]
            df_pod['count'] = 1
            df_pod = df_pod.groupby([df_pod.time], as_index=False, sort=False).agg(np.size)
            df_pod['trial'] = trial
            df_pod['count'] = df_pod['count'].cumsum()
            df_all_pod = df_all_pod.append(df_pod, sort=True, ignore_index=True)

            # Uniform Analysis
            filename = "analysis/results/Uniform_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            df_uni = pd.read_csv(filename)
            df_uni = df_uni[(df_uni.action == 'ENUMERATE_PROXY')].round()
            df_uni = df_uni[['time']]
            df_uni['count'] = 1
            df_uni = df_uni.groupby([df_uni.time], as_index=False, sort=False).agg(np.size)
            df_uni['trial'] = trial
            df_uni['count'] = df_uni['count'].cumsum()
            df_all_uni = df_all_uni.append(df_uni, sort=True, ignore_index=True)

            # Sandwich Analysis
            filename = "analysis/results/Sandwich_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            df_sand = pd.read_csv(filename)
            df_sand = df_sand[(df_sand.action == 'ENUMERATE_PROXY')].round()
            df_sand = df_sand[['time']]
            df_sand['count'] = 1
            df_sand = df_sand.groupby([df_sand.time], as_index=False, sort=False).agg(np.size)
            df_sand['trial'] = trial
            df_sand['count'] = df_sand['count'].cumsum()
            df_all_sandwich = df_all_sandwich.append(df_sand, sort=True, ignore_index=True)

    # Group each entry by ms time and trial number
    bin_array = np.linspace(0, 200, 21, endpoint=False)

    pod_bins = pd.cut(df_all_pod['time'], bin_array)
    df_all_pod = df_all_pod.groupby([pod_bins])
    uni_bins = pd.cut(df_all_uni['time'], bin_array)
    df_all_uni = df_all_uni.groupby([uni_bins])
    sand_bins = pd.cut(df_all_sandwich['time'], bin_array)
    df_all_sandwich = df_all_sandwich.groupby([sand_bins])

    # Select the maximum cumulative sum in each trial for each time slice
    grouped_uni = []
    grouped_pod = []
    grouped_sandwich = []
    data = [df_all_uni, df_all_pod, df_all_sandwich]
    data_groups = [grouped_uni, grouped_pod, grouped_sandwich]

    for df, group in zip(data, data_groups):
        for name, bin in df:
            max_list = bin.groupby(['trial'], as_index=False, sort=False)['count'].max()
            max = max_list['count'].tolist()
            group.append(max)

    # Create graph with all trials and experiments
    title="Number of proxies exposed over time in %d trials using %d proxies" % (util.NUM_TRIALS, util.NUM_PROXIES)
    fig, axes = plt.subplots(ncols=20, sharey=True, figsize=(17, 7))
    fig.subplots_adjust(wspace=0)
    #axes.set_xlabel("Binned Event Time (ms)")
    #axes.set_ylabel("Number of Total Exposed Proxies")
    fig.suptitle(title)

    # Setup arrays with the ranges for display
    data = {}
    names = {}
    lower = 0
    for i in range(0, 20):
        name = '%d' % lower
        names[i] = name
        data[name] = {}
        lower = lower + 10

    i = 0
    for k,v in data.items():
        v['U'] = grouped_pod[i]
        v['P'] = grouped_uni[i]
        v['S'] = grouped_sandwich[i]
        i = i+1
    bp_list = {}
    i = 0
    box_colors = ['lightgreen','lightblue','pink']
    for ax, name_index in zip(axes, names):
        name = names[name_index]
        bp_list[i] = ax.boxplot([data[name][item] for item in ['U', 'P','S']], patch_artist=True)
        for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
            plt.setp(bp_list[i][element], color="blue")
        box_num = 0
        for box in bp_list[i]['boxes']:
            box.set(color=box_colors[box_num], linewidth=2)
            box.set(facecolor=box_colors[box_num])
            box.set(hatch = '/')
            box_num = box_num + 1

        ax.set(xticklabels=['U', 'P','S'], xlabel=name)
        #ax.margins(0.05)
        plt.setp(ax.get_xticklabels(), rotation=45)
        i = i + 1

    #print(bp_list[0])
    #handles, labels = axes.flatten()[-2].get_legend_handles_labels()
    #axes.flatten()[-2].legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3)
    #print(handles)
    # TODO fig.legend(handles, labels, loc='upper center')
    plt.show()

if __name__ == '__main__':
    proxy_exposure_boxplot()
