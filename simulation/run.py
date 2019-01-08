import simulate_PoD
import pandas as pd

def run():
    client_arrival_rate = 1.0
    blocking_rate = 1.0
    service_time = 1.0
    num_proxies = 10
    queue_size = 10
    censor_bootstrap = 50
    seed = 42
    num_trials = 2
    sweep = 3
    TRACE = True
    trial = 0

    for i in range(0, num_trials):
        trial = trial + 1
        seed = seed + 1 # PRNG new sequence

        # Client arrival rate sweep
        for i in range(0, sweep):
            print(i)
            client_arrival_rate = client_arrival_rate + 1
            events = simulate_PoD.run(seed, client_arrival_rate, num_proxies, censor_bootstrap, TRACE)
            events_df = pd.DataFrame([vars(event) for event in events])
            if (TRACE):
                print(events_df)
            filename = "results/trial_%d_%d_sweep_%d_%d_%d.csv" % (trial, seed, client_arrival_rate, num_proxies, censor_bootstrap)
            events_df.to_csv(filename)

        # Number of proxies sweep


        # Censor Bootstrap period sweep

if __name__ == '__main__':
    run()
