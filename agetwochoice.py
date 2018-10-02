"""

Definitions for the environment and processes to model a two choice randomized
algorithm based on age selection preference used for proxy distribution

Two separate processes, the client arrival and blocking processes, share a proxy
system resource that centralizes the coordination of blocking and assignment events.

"""
import random
import simpy
import collections

SEED = 42                           # Answer to life, the universe, and everything
NUM_PROXIES = 10                    # Default number of total proxies
NUM_CLIENTS = 100                   # Total number of clients
CLIENT_ARRIVAL_MEAN = 10.0          # Average time (ms) in between client arrivals
CLIENT_ARRIVAL_SIGMA = 2.0          # Sigma for client arrival time
BLOCK_ARRIVAL_MEAN = 10.0           # Average time (ms) in between blocks
BLOCK_ARRIVAL_SIGMA = 2.0           # Sigma for blocking
SIM_TIME_MINS = 100 * 60/60         # 100 clients assigned one per second
MAXIMUM_LOAD = NUM_CLIENTS/NUM_PROXIES # default is m/n

# TODO move all this config stuff to a separate test case

def client_arrival_rate():
    """Clock time in between client arrivals."""
    return random.normalvariate(CLIENT_ARRIVAL_MEAN, CLIENT_ARRIVAL_SIGMA)

def single_block_rate():
    """Clock time between blocking events of single proxies."""
    # TODO this should be dependent upon the ratio of attackers to honest clients k/m
    return random.normalvariate(BLOCK_ARRIVAL_MEAN, BLOCK_ARRIVAL_SIGMA)

class Proxy(object):
    """
    A proxy's purpose in our model is to hold the assignment of clients.

    A proxy has an age value and a list of assigned clients.
    If blocked, the proxy should not know which client is responsible.
    """
    def __init__(self, env, name, age, clients):
        self.env = env
        self.name = name
        self.age = age
        self.clients = clients

class Client(object):
    """
    A client is assigned to a single proxy and randomly selected as corrupt.

    A client has an age of creation and an assigned proxy.
    The client can only block its assigned proxy.
    """

    def __init__(self, env, age, proxy, proxy_system):
        self.env = env
        self.age = age
        self.proxy = proxy
        self.malicious = random.choice([True, False])

        if self.malicious:
            # We assume all colluding insiders are controlled by the same censor.
            # Therefore, more than one malicious client assigned to the same
            # proxy does not increase the likelihood of blocking this proxy.
            if proxy not in proxy_system.vulnerable:
                proxy_system.vulnerable.add(proxy)
                print("added proxy to vulns")

def block_proxy(env, proxy_system):
    """
        A process that blocks proxies at a configurable rate.
        Randomly selects a proxy from the list of vulnerable_proxies that
        were assigned to malicious clients.
    """
    while True:
        yield env.timeout(single_block_rate())
        if proxy_system.vulnerable:
            proxy = random.choice(tuple(proxy_system.vulnerable))
            proxy_system.blocked.add(proxy)
            proxy_system.vulnerable.discard(proxy)
            proxy_system.proxies.discard(proxy)
            print('%d BLOCK Proxy "%s"' % (env.now, proxy.age))

def client_arrivals(env, proxy_system):
    """
    Centralized assignment of new clients until the sim time ends.
    """
    while True:
        # Normal function: choose 2 pseudorandom proxies to assign to client
        yield env.timeout(client_arrival_rate())
        if (proxy_system.proxies):
            proxy1 = random.choice(tuple(proxy_system.proxies))
            proxy2 = random.choice(tuple(proxy_system.proxies))
            # Assign the client to the youngest proxy
            if proxy1.age < proxy2.age:
                print('Client %d  --> Proxy %d' % (env.now, proxy1.age))
                proxy1.clients.add(Client(env, env.now, proxy1, proxy_system))
            else:
                print('Client %d --> Proxy %d' % (env.now, proxy2.age))
                proxy2.clients.add(Client(env, env.now, proxy2, proxy_system))
        else:
            print('Death of the system, all proxies are blocked')
            env.exit()

print('Starting the age based simulation')
random.seed(SEED)
env = simpy.Environment()

# sets to store proxy assignments with clients, vulnerable and blocked proxies
Assignments = collections.namedtuple('Assignments', ['stepwise', 'proxies', 'vulnerable', 'blocked'])
proxies = set(Proxy(env, 'Proxy %d' % i, i, set()) for i in range(NUM_PROXIES))
vulnerable = set()
blocked = set()

# Clients are assigned and proxies blocked as stepwise events
stepwise = simpy.Resource(env, capacity=1)
proxy_system = Assignments(stepwise, proxies, vulnerable, blocked)

# Start assignment and blocking processes and run
env.process(client_arrivals(env, proxy_system))
env.process(block_proxy(env, proxy_system))

env.run(until=10000)

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
