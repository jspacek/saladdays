import random
import simpy
import collections
import commons
import agetwochoice

SEED = 42                           # Answer to life, the universe, and everything
NUM_PROXIES = 100                   # Default number of total proxies
NUM_CLIENTS = 1000                  # Total number of clients
CLIENT_ARRIVAL_MEAN = 10.0          # Average time (ms) in between client arrivals
CLIENT_ARRIVAL_SIGMA = 2.0          # Sigma for client arrival time
# NOTE: Need to build up some proxy assignments before starting to block, otherwise the list won't fill up
BLOCK_ARRIVAL_MEAN = 200.0           # Average time (ms) in between blocks
BLOCK_ARRIVAL_SIGMA = 2.0           # Sigma for blocking
SIM_TIME = 10000                    # 100 clients assigned one per second

def client_arrival_rate():
    """Clock time in between client arrivals."""
    return random.normalvariate(CLIENT_ARRIVAL_MEAN, CLIENT_ARRIVAL_SIGMA)

def single_block_rate():
    """Clock time between blocking events of single proxies."""
    return random.normalvariate(BLOCK_ARRIVAL_MEAN, BLOCK_ARRIVAL_SIGMA)

print('Starting the age based simulation: normal state')
random.seed(SEED)
env = simpy.Environment()

# Collections for proxy assignments with clients, vulnerable, blocked proxies and events
Events = collections.namedtuple('Assignments', ['stepwise', 'proxies', 'vulnerable', 'blocked', 'events'])
proxies = set(commons.Proxy(env, 'Proxy %d' % i, i, set()) for i in range(NUM_PROXIES))
vulnerable = set()
blocked = set()
events = []

# Clients are assigned and proxies blocked as stepwise events
stepwise = simpy.Resource(env, capacity=1)
proxy_system = Events(stepwise, proxies, vulnerable, blocked, events)

# Start assignment and blocking processes and run
env.process(agetwochoice.client_assignment(env, proxy_system, client_arrival_rate()))
env.process(agetwochoice.proxy_block(env, proxy_system, single_block_rate()))

env.run(until=SIM_TIME)

# Analysis
print('Breakdown of events by time')

for event in events:
    print('%d "%s" "%s" "%s" "%s"' % (event.time, event.action, event.clientage, event.clientage, event.proxyname))

print('Ratio of malicious clients in each proxy')

for proxy in blocked:
    count = 0
    for client in proxy.clients:
        if client.malicious:
            count += 1
    print('%s %d out of %d clients are malicious' % (proxy.name, count, len(proxy.clients)))

print('%d Unblocked proxies' % (len(proxies)))
#for proxy in proxies:
    #print(proxy.name)

print('%d Vulnerable proxies' % (len(vulnerable)))
#for proxy in vulnerable:
    #print(proxy.name)

print('%d Blocked proxies' % (len(blocked)))
#for proxy in blocked:
    #print(proxy.name)

print('%d Unblocked invulnerable proxies' % (len(proxies - vulnerable)))
