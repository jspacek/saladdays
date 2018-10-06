import random

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
                print('Adding %s to the vulnerable list length of list %d' % (proxy.name, len(proxy_system.vulnerable)))
                proxy_system.vulnerable.add(proxy)

class Event(object):
    """
    Used as a container to store information about events for later analysis
    """
    def __init__(self, time, action, clientage, clientmalicious, proxyname, numblocked, numvulnerable, numsafe):
        self.time = time
        self.action = action
        self.clientage = clientage
        self.clientmalicious = clientmalicious
        self.proxyname = proxyname
        self.numblocked = numblocked
        self.numvulnerable = numvulnerable
        self.numsafe = numsafe
