import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.append('.')
from core import util
from simulation import simulate_PoD

def collateral_damage_scatterplot():
    """
     As clients join more rapidly or censor delays blocking, more collateral_damage is observed
    """
    print("________________________________Collateral Damage____________________________________\n")


    seed = util.SEED
    trial = 0
    df_all_pod = pd.DataFrame(columns=['time','cum_sum'])
    df_all_uni = pd.DataFrame(columns=['time','cum_sum'])
    df_all_sand = pd.DataFrame(columns=['time','cum_sum'])

    for i in range(0, util.NUM_TRIALS):
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
            df_pod = df_pod[['time','honest_clients']]
            df_pod = df_pod[(df_pod.honest_clients >= 0)]
            df_pod = df_pod.assign(cum_sum=df_pod.honest_clients.cumsum())
            df_all_pod = df_all_pod.append(df_pod)
            plt.scatter(df_pod.time, df_pod.cum_sum, c="g", marker="o", edgecolors="black", alpha="0.7", label="Power of D Choices")

            # Uniform Random analysis
            filename = "analysis/results/Uniform_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            #print(filename)
            df_uni = pd.read_csv(filename)
            # Filter file for relevant information
            df_uni = df_uni[['time','honest_clients']]
            df_uni = df_uni[(df_uni.honest_clients >= 0)]
            df_uni = df_uni.assign(cum_sum=df_uni.honest_clients.cumsum())
            df_all_uni = df_all_uni.append(df_uni)
            plt.scatter(df_uni.time, df_uni.cum_sum, c="r", marker="^", edgecolors="black", alpha="0.7", label="Uniform Random")

            # Sandwich analysis
            filename = "analysis/results/Sandwich_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            #print(filename)
            df_sand = pd.read_csv(filename)
            # Filter file for relevant information
            df_sand = df_sand[['time','honest_clients']]
            df_sand = df_sand[(df_sand.honest_clients >= 0)]
            df_sand = df_sand.assign(cum_sum=df_sand.honest_clients.cumsum())
            df_all_sand = df_all_sand.append(df_sand)
            plt.scatter(df_sand.time, df_sand.cum_sum, c="m", edgecolors="black", alpha="0.7", marker="*", label="Sandwich")

            title="Collateral Damage: Trial_%d_%d_sweep_%d_%d_%d" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            plt.title(title)
            plt.xlabel("Event Time")
            plt.ylabel("Number of Honest Clients")
            plt.legend(loc='upper left')
            #plt.show()
            graphname = "analysis/graphs/trial_%d_%d_sweep_%d_%d_%d.png" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            plt.savefig(graphname)
            plt.close()
            client_arrival_rate = client_arrival_rate + 1

    # Create graph with all trials and experiments
    title="Collateral Damage: %d Trials sweep_%d_%d_%d" % (util.NUM_TRIALS, util.SWEEP, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
    plt.title(title)
    plt.xlabel("Event Time")
    plt.ylabel("Number of Honest Clients")
    plt.scatter(df_all_pod.time, df_all_pod.cum_sum, c="g", edgecolors="black", marker="o", label="Power of D Choices", alpha="0.7")
    plt.scatter(df_all_uni.time, df_all_uni.cum_sum, c="r", edgecolors="black", marker="^", label="Uniform Random", alpha="0.7")
    plt.scatter(df_all_sand.time, df_all_sand.cum_sum, c="m", edgecolors="black", marker="*", label="Sandwich", alpha="0.7")
    plt.legend(loc='upper left')
    #print(df_all_uni)
    #print(df_all_pod)
    #plt.show()
    graphnamesvg = "analysis/graphs/%d_trials_sweep_%d_%d_%d.svg" % (util.NUM_TRIALS, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
    graphnamepng = "analysis/graphs/%d_trials_sweep_%d_%d_%d.png" % (util.NUM_TRIALS, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
    print("save png")
    plt.savefig(graphnamepng)
    print("save svg")
    plt.savefig(graphnamesvg, format='svg', dpi=1200)
    plt.close()

if __name__ == '__main__':
    collateral_damage_scatterplot()
