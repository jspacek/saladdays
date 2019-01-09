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
    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        seed = seed + 1
        client_arrival_rate = util.CLIENT_ARRIVAL_RATE

        # Client arrival rate sweep, create one graph per sweep
        for j in range(0, util.SWEEP):
            print(j)
            filename = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            print(filename)
            df = pd.read_csv(filename)
            # Filter file for only relevant information
            df = df[['time','honest_clients']]
            df = df[(df.honest_clients >= 0)]
            print(df)
            df.cumsum  = df.honest_clients.cumsum()

            print(df)
            print(len(df.time))
            print(len(df.honest_clients))
            print(len(df.cumsum))

            #print(len(df.cumsum))
            #plt.scatter(x, y, s, c="g", alpha=0.5, marker=r'$\clubsuit$',
                #    label="Luck")
            #plt.xlabel("Leprechauns")
            #plt.ylabel("Gold")
            #plt.legend(loc='upper left')
            plt.scatter(df.time, df.cumsum, c="g")
            plt.show()


            client_arrival_rate = client_arrival_rate + 1


if __name__ == '__main__':
    collateral_damage_scatterplot()
