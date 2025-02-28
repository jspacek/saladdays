import random
import simpy
import math
import sys
sys.path.append('.')
from core import util

# M/M/c/k Jackson network queue model
# Assign clients to proxies using power of 2 choices (aka Power of D Choices)

queue_size = 10
service_time = 1.0
blocking_rate = 1.0

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
    proxy = distributor.assign(client, censor)

    # Contact censor if the client is malicious, otherwise record client exposure
    # if the proxy is already enumerated
    if (malicious):
        censor.enumerate(proxy)
    elif (proxy in censor.proxies):
        event = util.create_event(arrival, "EXPOSE_CLIENT", distributor.proxies, distributor.blocked, proxy, 0)
        distributor.add_event(event)

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
        self.distributor_time = 0
        self.total_honest_clients = 0
        self.total_malicious_clients = 0
        self.next_q = 1
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

    def add_event(self, event):
        self.events.append(event)

    def assign(self, client, censor):
        assigned = self.env.now
        self.distributor_time = self.distributor_time + 1
        if (client.malicious):
            self.total_malicious_clients = self.total_malicious_clients + 1
        else:
            self.total_honest_clients = self.total_honest_clients + 1
        print(self.distributor_time)
        print("censor has %d proxies %d malicious %d honest " % (len(censor.proxies), self.total_malicious_clients, self.total_honest_clients))
        self.log_assign(censor)

        # Randomly select two proxies from the list to assign to the client
        random_index_1 = random.randint(0,len(self.proxies)-1)
        random_index_2 = random.randint(0,len(self.proxies)-1)

        random_proxy_1 = self.proxies[random_index_1]
        random_proxy_2 = self.proxies[random_index_2]
        # Branch process to service the client based on shorter queue (less historical load)
        if (len(random_proxy_1.queue) > len(random_proxy_2.queue)):
            self.env.process(random_proxy_2.service(client))
            return random_proxy_2
        else:
            self.env.process(random_proxy_1.service(client))
            return random_proxy_1

    def log_assign(self, censor):
        # Stop the experiment if there are no more unexposed or unblocked proxies
        if (util.CENSOR_BLOCK and len(self.proxies) == 0):
            if (self.trace):
                print("NO MORE UNBLOCKED PROXIES")
            self.env.exit()
        elif (len(censor.proxies) == len(self.proxies)):
            if (self.trace):
                print("NO MORE UNEXPOSED PROXIES")
            event = util.create_relative_event(self.distributor_time, "CENSOR_TRACK", self.proxies, censor.proxies, self.total_honest_clients, self.total_malicious_clients)
            self.events.append(event)
            # Final log of all proxies and clients before exiting
            for i in range(0, len(censor.proxies)):
                event = util.create_event(self.distributor_time, "PROXY_TRACK", self.proxies, censor.proxies, censor.proxies[i],0)
                self.events.append(event)
            self.env.exit()

        # log every 10th step in enumerated proxies
        if (len(censor.proxies) == self.next_q*(util.NUM_PROXIES/10)):
           event = util.create_relative_event(self.distributor_time, "CENSOR_TRACK", self.proxies, censor.proxies, self.total_honest_clients, self.total_malicious_clients)
           self.events.append(event)
           self.next_q = self.next_q + 1

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

        event = util.create_event(time, action, self.proxies, self.blocked, proxy, system_health)
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
        if (util.CENSOR_BLOCK):
            env.process(self._block())

    def _block(self):
        yield self.env.timeout(self.bootstrap)
        # Censor prioritizes blocks by larger queue size to maximize collateral damage
        while(True):
            if (len(self.proxies) > 0):
                self.proxies.sort(key=lambda p: len(p.queue), reverse=True)
                block_proxy = self.proxies[0]
                block_proxy.block()
                self.blocked.append(block_proxy)
                self.proxies.remove(block_proxy)

            t = random.expovariate(1.0 / blocking_rate)
            yield self.env.timeout(t)

    def enumerate(self, proxy):
        time = self.env.now
        system_health = 0
        if (proxy not in self.proxies and proxy not in self.blocked):
            self.proxies.append(proxy)
            action = "ENUMERATE_PROXY"
        else:
            # Censor deployed a client and received a proxy it already knew about
            action = "MISS_ENUMERATE_PROXY"

        event = util.create_event(time, action, self.proxies, self.blocked, proxy, system_health)
        self.events.append(event)

    def __str__(self):
        return self.proxies + " \n".join(self.blocked)

def run(seed, client_arrival_rate, num_proxies, censor_bootstrap, trace):
    random.seed(seed)
    env = simpy.Environment()

    distributor = Distributor(env, [], [], [], num_proxies, trace)
    censor = Censor(env, [], [], [], censor_bootstrap)

    env.process(generate_clients(env, client_arrival_rate, distributor, censor, trace))
    env.run() # run until system is dead (all proxies enumerated)

    return distributor.events + censor.events

if __name__ == '__main__':
    pass
