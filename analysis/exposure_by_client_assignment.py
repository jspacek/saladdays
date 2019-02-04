import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')
from core import util

def exposure_by_client_assignment():
    """
     Track the total proxy exposure by client assignments comparing 3 algorithms
    """
    print("________________________________ Proxy Exposure measured by Client Assignment ____________________________________\n")

    seed = util.SEED
    trial = 0
    df_all = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]

    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        seed = seed + 1
        client_arrival_rate = util.CLIENT_ARRIVAL_RATE
        uni_file = "analysis/results/Uniform_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
        pod_file = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
        teeter_file = "analysis/results/Teeter_trial_%d_%d_sweep_%d_%d_%d_victim_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP, util.VICTIM_LIST)
        files = [uni_file, pod_file, teeter_file]

        for i in range(0, len(df_all)):
            df = pd.read_csv(files[i])
            #print(files[i])
            df = df[(df.action == 'CENSOR_TRACK')]
            df = df[['time','action','total_blocked']]
            df = df.sort_values(by=['time'])
            df['trial'] = trial
            #print(df)
            df_all[i] = df_all[i].append(df, sort=False, ignore_index=True)

    labels = ['Uniform Random', 'Power of D Choices', 'Teetering']

    for i in range(0, len(df_all)):
        df_all[i] = df_all[i].groupby('total_blocked', as_index=False, sort=False)['time'].median()

    plt.gca().set_color_cycle(['blue', 'green', 'purple'])
    plt.plot(df_all[0].time, df_all[0].total_blocked)
    plt.plot(df_all[1].time, df_all[1].total_blocked)
    plt.plot(df_all[2].time, df_all[2].total_blocked)
    plt.xticks(np.arange(0, 2500, step=100), rotation=45)
    plt.legend([labels[0], labels[1], labels[2]], loc='upper left')
    title="Proxy Exposure by Client Assignment in %d trials using %d proxies with victim list size 1/%d" % (util.NUM_TRIALS, util.NUM_PROXIES, util.VICTIM_LIST)
    plt.title(title)
    plt.xlabel('Total number of client assignments')
    plt.ylabel('Total number of exposed proxies')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    #plt.show()
    graphnamepng = "analysis/archive/proxy_exposure_by_client_assignment%d_trials_%d_proxies_%d_victim_list.png" % (util.NUM_TRIALS, util.NUM_PROXIES, util.VICTIM_LIST)
    plt.savefig(graphnamepng)
    #plt.savefig(graphnamesvg, format='svg', dpi=1200)

if __name__ == '__main__':
    exposure_by_client_assignment()
