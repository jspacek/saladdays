"""

Definitions for the environment and processes to model the lower bound for proxy
distribution where the maximum load of each proxy is distributed in one proxy
known as bin packing. One proxy is selected to be blocked.

The client assignment and blocking processes are configured by the calling script.
They share a proxy system resource that centralizes the coordination of blocking and assignment events.

"""
import random
import simpy
import collections
import commons

def proxy_block(env, proxy_system, single_block_rate):
    """
        A process that blocks proxies at a configurable rate.
        Randomly selects a proxy from the list of vulnerable_proxies that
        were assigned to malicious clients.

        We examine how likely it is that the one proxy is blocked
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
    # Choose 1 single proxy to assign to client
    proxy = random.choice(tuple(proxy_system.proxies))

    while True:
        yield env.timeout(client_arrival_rate)
        if (proxy_system.proxies):
            # Assign the client to the single proxy
            print('Client %d --> Proxy %d' % (env.now, proxy.age))
            proxy.clients.add(commons.Client(env, env.now, proxy, proxy_system))
        else:
            print('Death of the system, all proxies are blocked')
            env.exit()
