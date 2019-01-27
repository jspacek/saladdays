import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')
from core import util
from simulation import simulate_PoD

def proxy_exposure_boxplot():
    """
     Track the total of enumerated proxies over time comparing 3 algorithms in a boxplot
    """
    print("________________________________Proxy Exposure____________________________________\n")

    seed = util.SEED
    trial = 0
    total_bins = 20
    bin_increment = 20
    df_all = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]

    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        seed = seed + 1
        client_arrival_rate = util.CLIENT_ARRIVAL_RATE
        uni_file = "analysis/results/Uniform_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
        pod_file = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
        sandwich_file = "analysis/results/Sandwich_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
        files = [uni_file, pod_file, sandwich_file]

        for i in range(0, len(df_all)):
            df = pd.read_csv(files[i])
            df = df[(df.action == 'ENUMERATE_PROXY')].round()
            df = df[['time']]
            df['count'] = 1
            df = df.groupby([df.time], as_index=False, sort=False).agg(np.size)
            df['trial'] = trial
            df['count'] = df['count'].cumsum()
            df_all[i] = df_all[i].append(df, sort=True, ignore_index=True)

    # Group each entry by ms time and trial number
    bin_array = np.linspace(0, 400, total_bins+1, endpoint=False)
    df_all_pod = df_all[0].groupby([pd.cut(df_all[0]['time'], bin_array)])
    df_all_uni = df_all[1].groupby([pd.cut(df_all[1]['time'], bin_array)])
    df_all_sandwich = df_all[2].groupby([pd.cut(df_all[2]['time'], bin_array)])

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
    fig, axes = plt.subplots(ncols=total_bins, sharey=True, figsize=(17, 7))
    fig.subplots_adjust(wspace=0.07)
    fig.suptitle(title)
    # Custom legend
    box_colors = ['lightgreen','lightblue','pink']
    labels = ['Uniform Random', 'Power of D Choices', 'Sandwich']
    uni_legend = mpatches.Patch(color=box_colors[0])
    pod_legend = mpatches.Patch(color=box_colors[1])
    sand_legend = mpatches.Patch(color=box_colors[2])
    fig.legend(handles=[uni_legend, pod_legend, sand_legend], labels=labels, loc="upper left")
    fig.text(0.5, 0.04, 'Binned Event Time (ms)', ha='center')
    fig.text(0.04, 0.5, 'Number of Total Exposed Proxies', va='center', rotation='vertical')

    # Setup arrays with the ranges for display in subplot bins
    data = {}
    names = {}
    lower = 0
    for i in range(0, total_bins):
        name = '%d' % lower
        names[i] = name
        data[name] = {}
        lower = lower + bin_increment

    i = 0
    for k,v in data.items():
        v['U'] = grouped_pod[i]
        v['P'] = grouped_uni[i]
        v['S'] = grouped_sandwich[i]
        i = i+1
    bp_list = {}
    i = 0
    for ax, name_index in zip(axes, names):
        name = names[name_index]
        bp_list[i] = ax.boxplot([data[name][item] for item in ['U', 'P','S']], patch_artist=True)
        for element in ['whiskers', 'fliers', 'means', 'medians', 'caps']:
            plt.setp(bp_list[i][element], color="black")
        box_num = 0
        for box in bp_list[i]['boxes']:
            box.set(color=box_colors[box_num], linewidth=2)
            box.set(facecolor=box_colors[box_num])
            box.set(hatch = '/')
            box_num = box_num + 1

        ax.set(xticklabels=['', '',''], xlabel=name)
        ax.margins(0)
        i = i + 1

    plt.show()

if __name__ == '__main__':
    proxy_exposure_boxplot()
