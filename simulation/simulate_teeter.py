import random
import simpy
import math
import sys
sys.path.append('.')
from core import util

# M/M/c/k Jackson network queue model
# The Teeter algorithm assigns clients to proxies using a victim list
# that is ordered by the total number of clients assigned historically
# The algorithm assigns clients to the most heavily loaded proxies first
# until a measure of "exposure" is reached (TODO)

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

    # TODO merged lambda rates for both honest and malicious to determine maliciousness of client
    malicious = random.choice([True, False])
    client = util.Client(name, malicious)

    # Call the distributor to assign a Proxy to the Client as a separate process
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
    def __init__(self, env, proxies, blocked, events, num_proxies, trace, sliding_window):
        self.env = env
        self.proxies = proxies
        self.blocked = blocked
        self.events = events
        self.num_proxies = num_proxies
        self.trace = trace
        self.sliding_window = sliding_window
        self.assignment_count = 0
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
        return self.teetering_algo(client)

    def teetering_algo(self, client):
        # Perform sort to order list by largest number of assignments (maximum load)
        sorted_proxies = sorted(self.proxies, key=lambda p: len(p.queue), reverse=True)
        victim_proxies = []
        # Size of the victim list is a fraction of the total proxies
        victim_size = (int)(len(self.proxies)/util.VICTIM_LIST)
        if (victim_size > 0):
            # Choose randomly from the top most heavily loaded proxies
            # Selecting only from a fraction of the victim list
            # Note: the selection is random to avoid predictability in the selection
            num_proxies = len(self.proxies)
            i = self.sliding_window % num_proxies
            j = (self.sliding_window + victim_size - 1) % num_proxies
            random_interval = random.randint(0, (victim_size-1))
            random_index = (random_interval + i) % num_proxies
            random_proxy_victim = self.proxies[random_index]
            print("sliding window i= %d j=%d selected %d has %d clients" % (i, j, random_index, len(random_proxy_victim.queue)))
            self.env.process(random_proxy_victim.service(client))
            # After some x assignments, slide the window
            self.assignment_count = self.assignment_count + 1
            if (self.assignment_count % util.SLIDING_WINDOW_INCREMENT == 0):
                self.sliding_window = self.sliding_window + 1
            return random_proxy_victim
        else:
            print("victim window too small")
            return self.proxies[0]

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
                global panic_level
                # Note: this strategy operates based on the blocking behaviour,
                # the distributor won't know how many proxies are enumerated (exposed)
                # TODO: how does this affect the analysis if we aren't analyzing block rate, eg. not a time series?
                if (len(self.blocked) > len(self.proxies)):
                    panic_level = panic_level + 1
                    #print("panic level is %d" % panic_level)

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
            print("size of proxies %d " % len(self.proxies))
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

    distributor = Distributor(env, [], [], [], num_proxies, trace, 0)
    censor = Censor(env, [], [], [], censor_bootstrap)

    env.process(generate_clients(env, client_arrival_rate, distributor, censor, trace))
    env.run() # run until system is dead (all proxies enumerated)

    return distributor.events + censor.events

if __name__ == '__main__':
    pass
