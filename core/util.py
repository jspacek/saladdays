# Default values for trials
NUM_TRIALS = 20
SEED = 42 # Fixes random state for reproducibility
SWEEP = 1
CLIENT_ARRIVAL_RATE = 1.0
NUM_PROXIES = 200
CENSOR_BOOTSTRAP = 50
TRACE = False
VICTIM_LIST = 20 # fraction of proxies sorted by maximum load
CENSOR_BLOCK = False # flag to control blocking on/off
SLIDING_WINDOW_INIT = 0 # where to start the sliding window of the teeter algorithm

class Event(object):
    """
    An event is recorded when a proxy is blocked
    A collection of static events is used for statistics
    """
    def __init__(self, time, action, proxy_name, total_blocked, total_healthy,
        honest_clients, malicious_clients, system_health):

        self.time = time
        self.action = action
        self.proxy_name = proxy_name
        self.total_blocked = total_blocked
        self.total_healthy = total_healthy
        self.honest_clients = honest_clients
        self.malicious_clients = malicious_clients
        self.system_health = system_health

    def __str__(self):
        return  self.time.join(self.action.join(proxy_name))

def create_event(time, action, proxies, blocked_or_enum, proxy, system_health):
    total_healthy = len(proxies) - len(blocked_or_enum)
    honest_clients = 0
    for client in proxy.queue:
        if (not client.malicious):
            honest_clients = honest_clients + 1
    malicious_clients = len(proxy.queue) - honest_clients
    event = Event(time, action, proxy.name, len(blocked_or_enum), total_healthy, honest_clients, malicious_clients, system_health)
    return event

def create_simple_event(time, action, proxies, blocked_or_enum):
    total_healthy = len(proxies) - len(blocked_or_enum)
    event = Event(time, action, "", len(blocked_or_enum), total_healthy, 0, 0, 0)
    return event

class Client(object):
    """
    A client is honest or malicious
    """
    def __init__(self, name, malicious):
        self.name = name
        self.malicious = malicious

    def __str__(self):
        return self.name + " ".join(self.malicious)


class Proxy(object):
    """
    A proxy places clients in its queue.
    If queue limit is reached, clients are balked.
    The size of a server's queue at the end of the experiment is the maximum load
    """
    def __init__(self, env, name, queue_size, service_time, creation, blocked, distributor, random, trace):
        self.env = env
        self.name = name
        self.queue = []
        self.service_time = service_time
        self.creation = creation
        self.blocked = blocked
        self.distributor = distributor
        self.trace = trace
        self.random = random

    def service(self, client):
        self.queue.append(client)

        # Calculate service time and yield when complete
        yield_time = self.random.expovariate(1.0 / self.service_time)
        yield self.env.timeout(yield_time)

        completed = self.env.now
        if (self.trace):
            print("%7.4f %s assigned to %s" % (completed, self.name, client.name))

    def block(self):
        self.blocked = True
        self.distributor.notify_block(self)

    def __str__(self):
        return self.name + " ".join(self.creation) + " ".join(self.blocked)
