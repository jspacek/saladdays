import random
import simpy
import math
import numpy as np

# A Jackson Network of M/M/c/n queues that switched between power of d choice and uniform probability distribution
# Client arrivals, censor blocking rate and service time are poisson process (exponential interarrival times)
# Probability that a client is malicious is uniform random
# c is the number of proxies
# n is the size of each individual proxy queue, i.e. load

client_arrival_rate = 3.0 # 200 per half hour in clients/minute
blocking_rate = 2.0
service_time = 3.0 # process servers time in minutes
num_proxies = 10
queue_size = 10
sim_time = 80 # in minutes
censor_bootstrap = 5
seed = 47
TRACE = True

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
    if (TRACE):
        print("%7.4f New Client %s" % (arrival, name))

    # call the distributor to assign a Proxy to the Client as a separate process
    # Determine maliciousness of client uniform randomly
    # (TODO this should instead be linked to the P of censor deploying malicious clients)
    malicious = random.choice([True, False])
    client = Client(name, malicious)
    proxy = distributor.assign(client)

    # Contact censor if the client is malicious
    if (malicious):
        censor.enumerate(proxy)


class Client(object):
    """
    A client is honest or malicious
    """
    def __init__(self, name, malicious):
        self.name = name
        self.malicious = malicious

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
        if (TRACE):
            print("%7.4f Bootstrap " % creation )
            print("number of proxies = %d" % num_proxies)
        for i in range(num_proxies):
            name = 'Proxy %d' % i
            proxy = Proxy(env, name, queue_size, service_time, creation, False, self)
            self.proxies.append(proxy)
            if (TRACE):
                print("%7.4f New Proxy %s" % (creation, name))

    def assign(self, client):
        assigned = env.now

        if (len(self.proxies) == 0):
            print("NO MORE PROXIES")
            env.exit()
        # Randomly select two proxies from the list to assign to the client
        random_index_1 = random.randint(0,len(self.proxies)-1)
        random_index_2 = random.randint(0,len(self.proxies)-1)

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

    def notify_block(self, proxy):
        time = self.env.now
        total_healthy = 0
        system_health = 0
        honest_clients = 0
        if (proxy in self.blocked):
            # Log a blocking miss event, unlikely to happen if the censor is smart
            total_healthy = len(self.proxies) - len(self.blocked)
            system_health = 1 - len(self.blocked)/len(self.proxies)
            event = Event(proxy.name, "MISS_PROXY_BLOCK", len(self.blocked), total_healthy, -1, -1, system_health, time)
            self.events.append(event)
        else:
            self.blocked.append(proxy)
            self.proxies.remove(proxy)
            # Log the blocking event
            if (len(self.proxies) == 0):
                print("in notifiy and it is DEAD")
            else:
                total_healthy = len(self.proxies) - len(self.blocked)
                system_health = 1 - len(self.blocked)/len(self.proxies)

            for client in proxy.queue:
                if (not client.malicious):
                    honest_clients = honest_clients + 1

            malicious_clients = len(proxy.queue) - honest_clients
            event = Event(proxy.name, "PROXY_BLOCK", len(self.blocked), total_healthy, honest_clients, malicious_clients, system_health, time)

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
        if (TRACE):
            print("%7.4f %s assigned to %s" % (completed, self.name, client.name))

    def block(self):
        self.blocked = True
        self.distributor.notify_block(self)

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
        # it should order by size of queue etc.
        while(True):
            # Assume the censor chooses a proxy to block uniform randomly
            if (len(self.proxies) > 0):
                random_index = random.randint(0,len(self.proxies)-1)
                block_proxy = self.proxies[random_index]

                block_proxy.block()
                self.blocked.append(block_proxy)
                self.proxies.remove(block_proxy)

            t = random.expovariate(1.0 / blocking_rate)
            yield env.timeout(t)


    def enumerate(self, proxy):
        time = env.now
        if (proxy not in self.proxies and proxy not in self.blocked):
            self.proxies.append(proxy)
            event = Event(proxy.name, "ENUMERATE_PROXY", -1, -1, -1, -1, -1, time)
            self.events.append(event)
        else:
            event = Event(proxy.name, "MISS_ENUMERATE_PROXY", -1, -1, -1, -1, -1, time)
            self.events.append(event)

class Event(object):
    """
    An event is recorded when a proxy is blocked
    A collection of static events is used for statistics
    """
    def __init__(self, proxy_name, action, total_blocked, total_healthy,
    honest_clients, malicious_clients, system_health, time):
        self.proxy_name = proxy_name
        self.action = action
        self.total_blocked = total_blocked
        self.total_healthy = total_healthy
        self.honest_clients = honest_clients
        self.malicious_clients = malicious_clients
        self.system_health = system_health
        self.time = time


print("**************** SIMULATION ****************")
print("Switch between Power of D choice to unbalanced in a M/M/c/n Network Queue")
print(""" client_arrival_rate=%f \n blocking_rate=%f \n service_time=%f
 num_proxies=%d \n queue_size=%d \n sim_time(minutes)=%f \n censor_bootstrap(minutes)=%f """ %
(client_arrival_rate, blocking_rate, service_time, num_proxies, queue_size, sim_time, censor_bootstrap))

print("********************************************")

# Run simulation
random.seed(seed)
env = simpy.Environment()
distributor = Distributor(env, [], [], [])
censor = Censor(env, [], [], [])
env.process(generate_clients(env, client_arrival_rate, distributor, censor))
env.run(until=sim_time)

print("**************** EVALUATION ****************")

print("**************** Collateral Damage ****************")
# proxies blocked with honest clients assigned
total_honest_clients = 0
total_malicious_clients = 0

for event in distributor.events:
    print("%7.4f %s %s honest_clients=%d malicious_clients=%d"
    % (event.time, event.action, event.proxy_name, event.honest_clients, event.malicious_clients))
    total_honest_clients = total_honest_clients + event.honest_clients
    total_malicious_clients = total_malicious_clients + event.malicious_clients

print("Total honest clients affected by proxy blocking = %d" % total_honest_clients)
collateral_damage = (total_honest_clients/ (total_honest_clients + total_malicious_clients)) * 100
print("Collateral damage = %f %%" % collateral_damage)

print("**************** Censor Resource Loss ****************")
# clients assigned to a proxy with another malicious client already assigned to it

total_client_misses = 0
for event in censor.events:
    if (event.action == "MISS_ENUMERATE_PROXY"):
        print("%7.4f %s %s" % (event.time, event.action, event.proxy_name))
        total_client_misses = total_client_misses + 1

print("Total censor resource loss = %d out of %d malicious clients" % (total_client_misses, total_malicious_clients))
print("Censor resource loss = %f %%" % ((total_client_misses/total_malicious_clients)*100))
print("**************** System Health ****************")





#total_in_queue = 0
#total_blocked = 0
#for proxy in distributor.proxies:
    #print("%s has %d clients, blocked = %s" % (proxy.name, len(proxy.queue), proxy.blocked))
    #total_in_queue = total_in_queue + len(proxy.queue)
