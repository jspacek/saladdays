import random
import simpy
import collections
import commons
import lowerbound

SEED = 42                           # Answer to life, the universe, and everything
NUM_PROXIES = 100                   # Default number of total proxies
NUM_CLIENTS = 1000                  # Total number of clients
CLIENT_ARRIVAL_MEAN = 10.0          # Average time (ms) in between client arrivals
CLIENT_ARRIVAL_SIGMA = 2.0          # Sigma for client arrival time
BLOCK_ARRIVAL_MEAN = 10.0           # Average time (ms) in between blocks
BLOCK_ARRIVAL_SIGMA = 2.0           # Sigma for blocking
SIM_TIME = 10000                    # 100 clients assigned one per second

def client_arrival_rate():
    """Clock time in between client arrivals."""
    return random.normalvariate(CLIENT_ARRIVAL_MEAN, CLIENT_ARRIVAL_SIGMA)

def single_block_rate():
    """Clock time between blocking events of single proxies."""
    return random.normalvariate(BLOCK_ARRIVAL_MEAN, BLOCK_ARRIVAL_SIGMA)

print('Starting the upper bound simulation')
random.seed(SEED)
env = simpy.Environment()

# Collections for proxy assignments with clients, vulnerable and blocked proxies
Assignments = collections.namedtuple('Assignments', ['stepwise', 'proxies', 'vulnerable', 'blocked'])
proxies = set(commons.Proxy(env, 'Proxy %d' % i, i, set()) for i in range(NUM_PROXIES))
vulnerable = set()
blocked = set()

# Clients are assigned and proxies blocked as stepwise events
stepwise = simpy.Resource(env, capacity=1)
proxy_system = Assignments(stepwise, proxies, vulnerable, blocked)

# Start assignment and blocking processes and run
env.process(lowerbound.client_assignment(env, proxy_system, client_arrival_rate()))
env.process(lowerbound.proxy_block(env, proxy_system, single_block_rate()))

env.run(until=SIM_TIME)

# Analysis
for proxy in proxies:
    print(proxy.age)
    for client in proxy.clients:
        print(client.malicious)

for proxy in vulnerable:
    print(proxy.age)
    for client in proxy.clients:
        print(client.malicious)

for proxy in blocked:
    print(proxy.age)
    for client in proxy.clients:
        print(client.malicious)
