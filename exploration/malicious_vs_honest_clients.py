import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')
from core import util

def malicious_vs_honest_clients():
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

        for i in range(2, 3):#len(df_all)):
            df = pd.read_csv(files[i])
            print(files[i])
            df = df[(df.action == 'PROXY_TRACK')]
            df = df[['time','action','total_blocked']]
            df = df.sort_values(by=['time'])
            df['trial'] = trial
            #print(df)
            df_all[i] = df_all[i].append(df, sort=False, ignore_index=True)

    labels = ['Uniform Random', 'Power of D Choices', 'Teetering']

    for i in range(0, len(df_all)):
        df_all[i] = df_all[i].groupby('total_blocked', as_index=False, sort=False)['time'].mean()

    malicious_medians = (20, 35, 30, 35, 27)
    honest_medians = (25, 32, 34, 20, 25)
    #menStd = (2, 3, 4, 1, 2)
    #womenStd = (3, 5, 2, 3, 3)
    #ind = np.arange(N)    # the x locations for the groups
    width = 0.35       # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, malicious_medians, width)#, yerr=menStd)
    p2 = plt.bar(ind, honest_medians, width, bottom=malicious_medians)#, yerr=womenStd)

    plt.ylabel('Scores')
    plt.title('Scores by group and gender')
    #plt.xticks(ind, ('G1', 'G2', 'G3', 'G4', 'G5'))
    #plt.yticks(np.arange(0, 81, 10))
    plt.legend((p1[0], p2[0]), ('Malicious Clients', 'Honest Clients'))

    plt.show()
    #graphnamepng = "analysis/archive/proxy_exposure_by_client_assignment%d_trials_%d_proxies_%d_victim_list.png" % (util.NUM_TRIALS, util.NUM_PROXIES, util.VICTIM_LIST)
    #plt.savefig(graphnamepng)
    #plt.savefig(graphnamesvg, format='svg', dpi=1200)

if __name__ == '__main__':
    malicious_vs_honest_clients()
