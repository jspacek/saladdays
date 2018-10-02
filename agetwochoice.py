"""

Definitions for the environment and processes to model a two choice randomized
algorithm based on age selection preference used for proxy distribution

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
        # Normal function: choose 2 pseudorandom proxies to assign to client
        yield env.timeout(client_arrival_rate)
        if (proxy_system.proxies):
            proxy1 = random.choice(tuple(proxy_system.proxies))
            proxy2 = random.choice(tuple(proxy_system.proxies))
            # Assign the client to the youngest proxy
            if proxy1.age < proxy2.age:
                print('Client %d  --> Proxy %d' % (env.now, proxy1.age))
                proxy1.clients.add(commons.Client(env, env.now, proxy1, proxy_system))
            else:
                print('Client %d --> Proxy %d' % (env.now, proxy2.age))
                proxy2.clients.add(commons.Client(env, env.now, proxy2, proxy_system))
        else:
            print('Death of the system, all proxies are blocked')
            env.exit()
