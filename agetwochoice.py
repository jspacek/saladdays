"""

Definitions for the environment and processes to model a two choice randomized
algorithm based on age selection preference used for proxy distribution

The client arrival and blocking processes are configured by the calling script.
They share a proxy system resource that centralizes the coordination of blocking and assignment events.

"""
import random
import simpy
import collections

class Proxy(object):
    """
    A proxy's purpose in our model is to hold the assignment of clients.

    A proxy has an age value and a list of assigned clients.
    If blocked, the proxy does not know which client is responsible.
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

def proxy_block(env, proxy_system, single_block_rate):
    """
        A process that blocks proxies at a configurable rate.
        Randomly selects a proxy from the list of vulnerable_proxies that
        were assigned to malicious clients.
    """
    while True:
        yield env.timeout(single_block_rate)
        if proxy_system.vulnerable:
            proxy = random.choice(tuple(proxy_system.vulnerable))
            proxy_system.blocked.add(proxy)
            proxy_system.vulnerable.discard(proxy)
            proxy_system.proxies.discard(proxy)
            print('%d BLOCK Proxy "%s"' % (env.now, proxy.age))

def client_assignment(env, proxy_system, client_arrival_rate):
    """
    Centralized assignment of new clients until the sim time ends.
    """
    while True:
        # Normal function: choose 2 pseudorandom proxies to assign to client
        yield env.timeout(client_arrival_rate)
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
