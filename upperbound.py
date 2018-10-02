"""

Definitions for the environment and processes to model the upper bound for proxy
distribution where the maximum load of each proxy is evenly distributed.

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
        # Choose 1 pseudorandom proxy to assign to client
        yield env.timeout(client_arrival_rate)
        if (proxy_system.proxies):
            proxy = random.choice(tuple(proxy_system.proxies))
            # Assign the client to the youngest proxy
            print('Client %d --> Proxy %d' % (env.now, proxy.age))
            proxy.clients.add(commons.Client(env, env.now, proxy, proxy_system))
        else:
            print('Death of the system, all proxies are blocked')
            env.exit()
