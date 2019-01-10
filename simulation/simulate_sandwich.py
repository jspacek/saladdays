import random
import simpy
import math
import sys
sys.path.append('.')
from core import util

# M/M/c/k Jackson network queue model
# Assign clients to proxies using power of 2 choices (aka Power of D Choices)
# When panic mode activated, switch to a victim set ordered by queue size
# Assign client to the heavily loaded proxies first

queue_size = 10
service_time = 1.0
blocking_rate = 1.0
panic_level = 0

def generate_clients(env, interval, distributor, censor, trace):
    counter = 0
    while(len(distributor.proxies) > 0): # infinite incoming clients
        name = 'Client %d' % counter
        client_arrival(env, name, distributor, censor, trace)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)
        counter = counter + 1

def client_arrival(env, name, distributor, censor, trace):
    arrival = env.now
    if (trace):
        print("%7.4f New Client %s" % (arrival, name))

    # call the distributor to assign a Proxy to the Client as a separate process
    # Determine maliciousness of client uniform randomly
    # (TODO this should instead be linked to the P of censor deploying malicious clients)
    malicious = random.choice([True, False])
    client = util.Client(name, malicious)
    proxy = distributor.assign(client)

    # Contact censor if the client is malicious
    if (malicious):
        censor.enumerate(proxy)

class Distributor(object):
    """
    A distributor creates proxies during bootstrap.
    It maintains a list of all proxies in the system and distributes proxies
    to clients based on uniform random selection.
    """
    def __init__(self, env, proxies, blocked, events, num_proxies, trace):
        self.env = env
        self.proxies = proxies
        self.blocked = blocked
        self.events = events
        self.num_proxies = num_proxies
        self.trace = trace
        self._bootstrap()

    def _bootstrap(self):
        creation = self.env.now
        if (self.trace):
            print("%7.4f Bootstrap " % creation )
            print("number of proxies = %d" % self.num_proxies)
        for i in range(self.num_proxies):
            name = 'Proxy %d' % i
            proxy = util.Proxy(self.env, name, queue_size, service_time, creation, False, self, random, self.trace)
            self.proxies.append(proxy)
            if (self.trace):
                print("%7.4f New Proxy %s" % (creation, name))

    def assign(self, client):
        assigned = self.env.now

        if (len(self.proxies) == 0):
            if (self.trace):
                print("NO MORE PROXIES")
            self.env.exit()
        # Randomly select two proxies from the list to assign to the client
        random_index_1 = random.randint(0,len(self.proxies)-1)
        random_index_2 = random.randint(0,len(self.proxies)-1)

        random_proxy_1 = self.proxies[random_index_1]
        random_proxy_2 = self.proxies[random_index_2]
        # TODO check that the queue is not full otherwise balk, or retry (a bit too complex? more enumeration to track?)
        # Branch process to service the client based on shorter queue (less historical load)
        if (panic_level > 0):
            #print("in panic mode %d" % panic_level)
            #print(assigned)
            # choose a victim proxy set *once* based on the current ordering of proxy load
            # Perform sort and return new list (not inplace)
            sorted_proxies = sorted(self.proxies, key=lambda p: len(p.queue), reverse=True)
            victim_proxies = []
            # size is a fraction of the total unblocked proxies
            victim_size = (int)(len(self.proxies)/util.VICTIM_SET)
            #print(victim_size)
            if (victim_size > 0):
                # choose randomly from the top most heavily loaded proxies
                # selecting only from a fraction of the victim set
                random_index_1 = random.randint(0,victim_size-1)
                random_proxy_1 = self.proxies[random_index_1]
                #print(random_proxy_1.name)
                self.env.process(random_proxy_1.service(client))
                return random_proxy_1
            else:
                return self.proxies[0]

        else:
            if (len(random_proxy_1.queue) > len(random_proxy_2.queue)):
                self.env.process(random_proxy_2.service(client))
                return random_proxy_2
            else:
                self.env.process(random_proxy_1.service(client))
                return random_proxy_1

    def notify_block(self, proxy):
        time = self.env.now
        system_health = 0
        if (proxy in self.blocked):
            # Unlikely to happen if the censor is smart
            action = "MISS_PROXY_BLOCK"
            system_health = (1-len(self.blocked)/(len(self.proxies)+len(self.blocked))) * 100
        else:
            self.blocked.append(proxy)
            self.proxies.remove(proxy)
            if (len(self.proxies) == 0):
                if (self.trace):
                    print("No more proxies available")
                action = "PROXY_DEATH"
            else:
                action = "PROXY_BLOCK"
                system_health = (1-len(self.blocked)/(len(self.proxies)+len(self.blocked))) * 100
                global panic_level
                if (len(self.blocked) > 2):#len(self.proxies)):
                    panic_level = panic_level + 1
                    #print("panic level is %d" % panic_level)

        total_healthy = len(self.proxies)
        honest_clients = 0
        for client in proxy.queue:
            if (not client.malicious):
                honest_clients = honest_clients + 1
        malicious_clients = len(proxy.queue) - honest_clients
        event = util.Event(time, action, proxy.name, len(self.blocked), total_healthy, honest_clients, malicious_clients, system_health)
        self.events.append(event)
        if (action == "PROXY_DEATH"):
            self.env.exit()

class Censor(object):
    """
    The censor listens for malicious clients to relay proxy information
    After an initial bootstrap period, it begins to block proxies
    """
    def __init__(self, env, proxies, blocked, events, bootstrap):
        self.env = env
        self.proxies = proxies
        self.blocked = blocked
        self.events = events
        self.bootstrap = bootstrap
        env.process(self._block())

    def _block(self):
        yield self.env.timeout(self.bootstrap)
        # Censor prioritizes blocks by larger queue size to maximize collateral damage
        while(True):
            if (len(self.proxies) > 0):
                self.proxies.sort(key=lambda p: len(p.queue), reverse=True)
                block_proxy = self.proxies[0]
                #print(len(block_proxy.queue))
                #print(len(self.proxies[-1].queue))
                block_proxy.block()
                self.blocked.append(block_proxy)
                self.proxies.remove(block_proxy)

            t = random.expovariate(1.0 / blocking_rate)
            yield self.env.timeout(t)

    def enumerate(self, proxy):
        time = self.env.now
        if (proxy not in self.proxies and proxy not in self.blocked):
            self.proxies.append(proxy)
            event = util.Event(time, "ENUMERATE_PROXY", proxy.name, -1, -1, -1, -1, -1)
            self.events.append(event)
        else:
            # Censor deployed a client and received a proxy it already knew about
            event = util.Event(time, "MISS_ENUMERATE_PROXY", proxy.name, -1, -1, -1, -1, -1)
            self.events.append(event)

    def __str__(self):
        return self.proxies + " \n".join(self.blocked)

def run(seed, client_arrival_rate, num_proxies, censor_bootstrap, trace):
    global panic_level
    panic_level = 0

    random.seed(seed)
    env = simpy.Environment()

    distributor = Distributor(env, [], [], [], num_proxies, trace)
    censor = Censor(env, [], [], [], censor_bootstrap)
    env.process(generate_clients(env, client_arrival_rate, distributor, censor, trace))

    env.run() # run until system is dead (no more unblocked proxies)

    return distributor.events + censor.events

if __name__ == '__main__':
    pass
