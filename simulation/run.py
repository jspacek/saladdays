import pandas as pd
import sys
sys.path.append('.')
#for p in sys.path:
    #print(p)
from core import util
import simulate_PoD

client_arrival_rate = 0
seed = 0
sweep = 0
censor_bootstrap = 0

def run():
    trial = 0
    set_defaults()
    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        global seed
        seed = seed + trial # PRNG new sequence for new trial
        # Client arrival rate sweep
        for j in range(0, util.SWEEP):
            global client_arrival_rate
            # TODO run the uniform and sandwich simulations here too
            events = simulate_PoD.run(seed, client_arrival_rate, util.NUM_PROXIES, censor_bootstrap, util.TRACE)
            events_df = pd.DataFrame([vars(event) for event in events])
            events_df = events_df[['time','action','proxy_name','honest_clients','malicious_clients','system_health','total_blocked','total_healthy']]

            if (util.TRACE):
                print(events_df)
            filename = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            events_df.to_csv(filename)
            client_arrival_rate = client_arrival_rate + 1


        set_defaults()

        # Censor Bootstrap period sweep - Affects the # of honest clients that join a proxy)



def set_defaults():
    global seed
    seed = util.SEED
    global sweep
    sweep = util.SWEEP
    global client_arrival_rate
    client_arrival_rate = util.CLIENT_ARRIVAL_RATE
    global censor_bootstrap
    censor_bootstrap = util.CENSOR_BOOTSTRAP

if __name__ == '__main__':
    run()
