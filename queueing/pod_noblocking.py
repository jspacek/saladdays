import random
import simpy
import math
import numpy as np

# A Jackson Network of M/M/c/n queues with power of d choice probability distribution
# Client arrivals and service time are poisson process (exponential interarrival times)
# c is the number of proxies
# n is the size of each individual proxy queue, i.e. load

client_arrival_rate = 3.333333333333 # 200 per half hour in clients/minute
service_time = 3.0 # process servers time in minutes
num_proxies = 12
queue_size = 10
sim_time = 60 # in minutes
seed = 42

def generate_clients(env, interval, distributor):
    counter = 0
    while(True): # infinite incoming clients
        name = 'Client %d' % counter
        client_arrival(env, name, distributor)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)
        counter = counter + 1

def client_arrival(env, name, distributor):
    arrival = env.now
    print("%7.4f New Client %s" % (arrival, name))

    # call the distributor to assign a Proxy to the Client as a separate process
    distributor.assign(name)

class Distributor(object):
    """
    A distributor creates proxies during bootstrap.
    It maintains a list of all proxies in the system and distributes proxies
    to clients based on uniform random selection.
    """
    def __init__(self, env, proxies, metrics):
        self.env = env
        self.proxies = proxies
        self.metrics = metrics
        self._bootstrap()

    def _bootstrap(self):
        creation = env.now
        print("%7.4f Bootstrap " % creation )

        for i in range(num_proxies):
            name = 'Proxy %d' % i
            proxy = Proxy(env, name, queue_size, service_time, creation)
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
        else:
            env.process(random_proxy_1.service(client))


class Proxy(object):
    """
    A proxy places clients in its queue.
    Following the Erlang-C formula, the clients do not exit the queue.
    If queue limit is reached, clients are balked.
    The size of a server's queue at the end of the experiment is the maximum load
    """
    def __init__(self, env, name, queue_size, service_time, creation):
        self.env = env
        self.name = name
        self.queue = []
        self.service_time = service_time
        self.creation = creation

    def service(self, client):
        self.queue.append(client)

        # Calculate service time and yield when complete
        yield_time = random.expovariate(1.0 / service_time)
        yield self.env.timeout(yield_time)

        completed = env.now
        print("%7.4f %s assigned to %s" % (completed, self.name, client))


print('Uniform Random M/M/c/n Network Queue')
print("**************** Simulation ****************")

random.seed(seed)
env = simpy.Environment()
counter = simpy.Resource(env, capacity=1)
distributor = Distributor(env, [], service_time)
env.process(generate_clients(env, client_arrival_rate, distributor))
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
for proxy in distributor.proxies:
    print("%s has %d clients" % (proxy.name, len(proxy.queue)))
    total_in_queue = total_in_queue + len(proxy.queue)

print("Total in all queues %d" % total_in_queue)
