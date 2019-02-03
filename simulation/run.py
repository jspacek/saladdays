import pandas as pd
import sys
sys.path.append('.')
#for p in sys.path:
    #print(p)
from core import util
import simulate_PoD
import simulate_uniform
import simulate_teeter

# Global parameters used for sweeping
client_arrival_rate = 0
seed = 0
sweep = 0
censor_bootstrap = 0

def run():
    trial = 0
    set_defaults()
    for i in range(0, util.NUM_TRIALS):
        trial = trial + 1
        print("*******************TRIAL************************")
        print(trial)
        global client_arrival_rate
        global seed
        set_defaults()
        seed = seed + trial # PRNG new sequence for new trial

        # Client arrival rate sweep for Power of D choices
        for j in range(0, util.SWEEP):
            events_pod = simulate_PoD.run(seed, client_arrival_rate, util.NUM_PROXIES, censor_bootstrap, util.TRACE)
            events_pod_df = pd.DataFrame([vars(event) for event in events_pod])
            events_pod_df = events_pod_df[['time','action','proxy_name','honest_clients','malicious_clients','system_health','total_blocked','total_healthy']]

            if (util.TRACE):
                print(events_pod_df)
            filename = "analysis/results/PoD_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            events_pod_df.to_csv(filename)
            client_arrival_rate = client_arrival_rate + 1

        set_defaults()
        seed = seed + trial # PRNG new sequence for new trial

        # Client arrival rate sweep for uniform  choices
        for j in range(0, util.SWEEP):
            events_uni = simulate_uniform.run(seed, client_arrival_rate, util.NUM_PROXIES, censor_bootstrap, util.TRACE)
            events_uni_df = pd.DataFrame([vars(event) for event in events_uni])
            events_uni_df = events_uni_df[['time','action','proxy_name','honest_clients','malicious_clients','system_health','total_blocked','total_healthy']]

            if (util.TRACE):
                print(events_pod_df)
            filename = "analysis/results/Uniform_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            events_uni_df.to_csv(filename)
            client_arrival_rate = client_arrival_rate + 1

        set_defaults()
        seed = seed + trial # PRNG new sequence for new trial

        # Client arrival rate sweep for teeter algorithm
        for j in range(0, util.SWEEP):
            events_teeter = simulate_teeter.run(seed, client_arrival_rate, util.NUM_PROXIES, censor_bootstrap, util.TRACE)
            events_teeter_df = pd.DataFrame([vars(event) for event in events_teeter])
            events_teeter_df = events_teeter_df[['time','action','proxy_name','honest_clients','malicious_clients','system_health','total_blocked','total_healthy']]

            if (util.TRACE):
                print(events_pod_df)
            filename = "analysis/results/Teeter_trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, util.NUM_PROXIES, util.CENSOR_BOOTSTRAP)
            events_teeter_df.to_csv(filename)
            client_arrival_rate = client_arrival_rate + 1

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
