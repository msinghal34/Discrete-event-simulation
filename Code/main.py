import yaml
from event import *
from policy import *
from distribution import *
from server import *
from thread import *

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(config)
    except yaml.YAMLError as exc:
        print(exc)

NUM_CORES = config["num_cores"]     # Number of cores
NUM_THREADS = config["num_threads"]    # Number of threads in the system
BUFFER_CAPACITY = config["buffer_capacity"]     # Buffer Size
# Max length of the Request queue
MAX_REQUEST_QUEUE_LENGTH = config["max_request_queue_length"]
POLICY = config["policy"]   # Scheduling policy for picking requests
# Quantum size to run a process before context switch
QUANTUM_SIZE = config["quantum_size"]
NUM_USERS = config["num_users"]     # Num of users at the client station
# Context Switch Overhead
CONTEXT_SWITCH_OVERHEAD = config["context_switch_overhead"]
STOPPING_CRITERION = config["stopping_criterion"]   # number of requests to be generated

THINK_TIME_DIST = config["think_time_distribution"]
SERVICE_TIME_DIST = config["service_time_distribution"]
TIMEOUT_DIST = config["timeout_distribution"]

cores = []  # Cores in the system
for i in range(NUM_CORES):
    cores.append(Core(i, Buffer(BUFFER_CAPACITY), POLICY, QUANTUM_SIZE))
coreHandler = CoreHandler(cores)    # Core Handler Instance

EVENT_LIST = EventList()    # An instance of the event list
THREAD_LIST = ThreadList(NUM_THREADS)    # A Thread List instance
# An instance of Request queue
REQUEST_QUEUE = RequestQueue(MAX_REQUEST_QUEUE_LENGTH)

# Intialization of Event List
sim_time = 0.0  # Current Simulation Time
request_id = 0
for i in range(NUM_USERS):
    start_time = sim_time + \
        get_random_variate(THINK_TIME_DIST["name"], THINK_TIME_DIST["params"])
    timeout = get_random_variate(TIMEOUT_DIST["name"], TIMEOUT_DIST["params"])
    service_time = get_random_variate(
        SERVICE_TIME_DIST["name"], SERVICE_TIME_DIST["params"])
    EVENT_LIST.addEvent(event_type=EventType.create_request, start_time=start_time, event_attr={
                        "id": request_id, "timeout": timeout, "service_time": service_time})
    request_id += 1

# Main loop to process events until it is empty or the number of requests generated exceeds stopping criterion
while not (EVENT_LIST.isEmpty() or request_id > STOPPING_CRITERION):
    event = EVENT_LIST.getNextEvent()
    prev_sim_time = sim_time
    sim_time = event.start_time

    if event.event_type == EventType.create_request:
        request = Request(event.attr["id"],
                          event.attr["timeout"], event.attr["service_time"], event.start_time)