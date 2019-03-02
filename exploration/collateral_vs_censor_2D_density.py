import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import kde
import sys
sys.path.append('.')
from core import util

def collateral_vs_censor_2D_density():

    seed = util.SEED
    trial = 0
    files = []
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
            df = df[['time','honest_clients']]
            df['count_proxies'] = 1
            df = df.groupby([df.time], as_index=False, sort=False).agg(np.sum)
            df = df.sort_values(by=['time'])
            df['trial'] = trial
            df['count_proxies'] = df['count_proxies'].cumsum()
            df['honest_clients'] = df['honest_clients'].cumsum()

            df_all[i] = df_all[i].append(df, sort=True, ignore_index=True)

    titles = ['Uniform Random', 'Power of D Choices', 'Sandwich']

    nbins = 20
    fig, axes = plt.subplots(ncols=3, nrows=1, figsize=(21, 5))
    for i in (range(0,len(axes))):
        axes[i].set_title(titles[i])
        x = df_all[i].honest_clients
        y = df_all[i].count_proxies
        k = kde.gaussian_kde((x, y))
        xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
        zi = k(np.vstack([xi.flatten(), yi.flatten()]))
        axes[i].pcolormesh(xi, yi, zi.reshape(xi.shape), shading='gouraud', cmap=plt.cm.BuGn_r)
        axes[i].contour(xi, yi, zi.reshape(xi.shape))
        axes[i].set_xlabel('Number of Total Exposed Proxies')
        axes[i].set_ylabel('Number of Total Exposed (Honest) Clients')

    #plt.show()
    graphnamepng = "analysis/archive/collateral_vs_censor_%d_trials_%d_proxies.png" % (util.NUM_TRIALS, util.NUM_PROXIES)
    plt.savefig(graphnamepng)
    #plt.savefig(graphnamesvg, format='svg', dpi=1200)

if __name__ == '__main__':
    collateral_vs_censor_2D_density()
