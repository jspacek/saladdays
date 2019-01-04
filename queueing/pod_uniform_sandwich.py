import random
import simpy
import math
import numpy as np

# A Jackson Network of M/M/c/n queues that switched between power of d choice and uniform probability distribution
# Client arrivals, censor blocking rate and service time are poisson process (exponential interarrival times)
# Probability that a client is malicious is uniform random
# c is the number of proxies
# n is the size of each individual proxy queue, i.e. load

client_arrival_rate = 3.333333333333 # 200 per half hour in clients/minute
blocking_rate = 2
service_time = 3.0 # process servers time in minutes
num_proxies = 20
queue_size = 10
sim_time = 60 # in minutes
censor_bootstrap = 5
seed = 44

def generate_clients(env, interval, distributor, censor):
    counter = 0
    while(True): # infinite incoming clients
        name = 'Client %d' % counter
        client_arrival(env, name, distributor, censor)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)
        counter = counter + 1

def client_arrival(env, name, distributor, censor):
    arrival = env.now
    print("%7.4f New Client %s" % (arrival, name))

    # call the distributor to assign a Proxy to the Client as a separate process
    proxy = distributor.assign(name)

    # Determine maliciousness of client and contact censor
    malicious = random.choice([True, False])
    if (malicious):
        censor.enumerate(proxy)

class Distributor(object):
    """
    A distributor creates proxies during bootstrap.
    It maintains a list of all proxies in the system and distributes proxies
    to clients based on uniform random selection.
    """
    def __init__(self, env, proxies, blocked, events):
        self.env = env
        self.proxies = proxies
        self.blocked = blocked
        self.events = events
        self._bootstrap()

    def _bootstrap(self):
        creation = env.now
        print("%7.4f Bootstrap " % creation )

        for i in range(num_proxies):
            name = 'Proxy %d' % i
            proxy = Proxy(env, name, queue_size, service_time, creation, False, self)
            self.proxies.append(proxy)
            print("%7.4f New Proxy %s" % (creation, name))

    def assign(self, client):
        assigned = env.now

        # Randomly select two proxies from the list to assign to the client
        random_index_1 = random.randint(0,num_proxies-1)
        random_index_2 = random.randint(0,num_proxies-1)

        random_proxy_1 = self.proxies[random_index_1]
        random_proxy_2 = self.proxies[random_index_2]
        # TODO check that the queue is not full otherwise balk, or retry (a bit too complex? more enumeration to track?)
        # Branch process to service the client based on shorter queue (less historical load)
        if (len(random_proxy_1.queue) > len(random_proxy_2.queue)):
            env.process(random_proxy_2.service(client))
            return random_proxy_2
        else:
            env.process(random_proxy_1.service(client))
            return random_proxy_1

    def notify_block(self, name):
        time = self.env.now
        for proxy in self.blocked:
            print("blocked ", proxy.name)
        if (proxy in self.blocked):
            # Log a blocking miss event
            total_healthy = len(self.proxies) - len(self.blocked)
            system_health = 1 - len(self.blocked)/len(self.proxies)
            event = Event(proxy.name, "MISS_PROXY_BLOCK", len(self.blocked), total_healthy, -1, system_health, time)
            self.events.append(event)
        else:
            self.blocked.append(proxy)
            # Log the blocking event
            total_healthy = len(self.proxies) - len(self.blocked)
            system_health = 1 - len(self.blocked)/len(self.proxies)
            event = Event(proxy.name, "PROXY_BLOCK", len(self.blocked), total_healthy, -1, system_health, time)
            self.events.append(event)

class Proxy(object):
    """
    A proxy places clients in its queue.
    Following the Erlang-C formula, the clients do not exit the queue.
    If queue limit is reached, clients are balked.
    The size of a server's queue at the end of the experiment is the maximum load
    """
    def __init__(self, env, name, queue_size, service_time, creation, blocked, distributor):
        self.env = env
        self.name = name
        self.queue = []
        self.service_time = service_time
        self.creation = creation
        self.blocked = blocked
        self.distributor = distributor

    def service(self, client):
        self.queue.append(client)

        # Calculate service time and yield when complete
        yield_time = random.expovariate(1.0 / service_time)
        yield self.env.timeout(yield_time)

        completed = env.now
        print("%7.4f %s assigned to %s" % (completed, self.name, client))

    def block(self):
        self.blocked = True
        print("i am contacting the block ", self.name)
        self.distributor.notify_block(self.name)

class Censor(object):
    """
    The censor listens for malicious clients to relay proxy information
    After an initial bootstrap period, it begins to block proxies
    """
    def __init__(self, env, proxies, blocked, events):
        self.env = env
        self.proxies = proxies
        self.blocked = blocked
        self.events = events
        env.process(self._block())

    def _block(self):
        yield self.env.timeout(censor_bootstrap)
        # TODO this is not a very smart strategy for a censor to employ
        while(True):
            # Assume the censor chooses a proxy to block uniform randomly
            if (len(self.proxies) > 0):
                random_index = random.randint(0,len(self.proxies)-1)
                block_proxy = self.proxies[random_index]
                #if (block_proxy not in self.blocked):
                block_proxy.block()
                self.blocked.append(block_proxy)

            t = random.expovariate(1.0 / blocking_rate)
            yield env.timeout(t)


    def enumerate(self, proxy):
        time = env.now
        self.proxies.append(proxy)
        # TODO event calculations
        event = Event(proxy.name, "PROXY_ENUMERATED", -1, -1, len(self.proxies), -1, time)
        self.events.append(event)


class Event(object):
    """
    An event is recorded when a proxy is blocked
    A collection of static events is used for statistics
    """
    def __init__(self, proxy_name, action, total_blocked, total_healthy, total_enumerated, system_health, time):
        self.proxy_name = proxy_name
        self.action = action
        self.total_blocked = total_blocked
        self.total_healthy = total_healthy
        self.total_enumerated = total_enumerated
        self.system_health = system_health
        self.time = time


print('Uniform Random M/M/c/n Network Queue')
print("**************** Simulation ****************")

random.seed(seed)
env = simpy.Environment()
counter = simpy.Resource(env, capacity=1)
distributor = Distributor(env, [], [], [])
censor = Censor(env, [], [], [])
env.process(generate_clients(env, client_arrival_rate, distributor, censor))
env.run(until=sim_time)

print("**************** Evaluation ****************")
# Probability that the customer has to wait for service
# E = λ x h, λ = mean arrival rate, h = mean service time
erlangs = (client_arrival_rate * 60 * service_time)/60 # lambda/mu in hour or # clients per hour * service time in minutes
multiplicand = (math.pow(erlangs, num_proxies)/math.factorial(num_proxies)) * (num_proxies/(num_proxies-erlangs))
lmbd = [math.pow(erlangs, x)/math.factorial(x) for x in range(0, num_proxies)]
summation = sum(lmbd)
denominator = summation + multiplicand
Pw = multiplicand/denominator
print("Probability of waiting %f"% Pw)
# TODO Blocking probability for finite capacity queues

# Client load on each server
total_in_queue = 0
total_blocked = 0
for proxy in distributor.proxies:
    print("%s has %d clients, blocked = %s" % (proxy.name, len(proxy.queue), proxy.blocked))
    total_in_queue = total_in_queue + len(proxy.queue)

print("Events in Distributor")
for event in distributor.events:
    print("%7.4f %s %s total blocked=%d total healthy=%d system health=%f" % (event.time, event.action, event.proxy_name, event.total_blocked, event.total_healthy, event.system_health))

# TODO censor events

print("Total clients in all queues %d" % total_in_queue)
print("Total proxies blocked %d" % len(distributor.blocked))
