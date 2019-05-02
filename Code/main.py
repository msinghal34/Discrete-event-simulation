import sys
import os
import yaml

from event import *
from policy import *
from distribution import *
from server import *
from thread import *
from util import *

with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        print(config)
        printLineBreak()
    except yaml.YAMLError as exc:
        print(exc)

if config["verbose"] == 0:
    # Block all terminal prints
    sys.stdout = open(os.devnull, 'w')

NUM_RUNS = config["num_runs"]       # Number of runs
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

# List of sentences to put in file used for calculating metrics
info_list = []

def info(object):
    if type(object) == type(Thread):  # Request
        x = "\t" + str(object.request.id) + "\t" + str(object.request.timestamp)
        return x
    else:
        return "\t" + str(object.id)

# Main loop to process events until the number of requests generated exceeds stopping criterion
for z in range(NUM_RUNS):
    info_list.append(str("RUN" + "\t" + str(z)))
    
    # Init of each run
    cores = []  # Cores in the system
    for i in range(NUM_CORES):
        cores.append(Core(i, Buffer(i, BUFFER_CAPACITY), POLICY, QUANTUM_SIZE))
    core_handler = CoreHandler(cores)    # Core Handler Instance

    event_list = EventList()    # An instance of the event list
    thread_list = ThreadList(NUM_THREADS)    # A Thread List instance
    # An instance of Request queue
    request_queue = RequestQueue(MAX_REQUEST_QUEUE_LENGTH)

    sim_time = 0.0  # Current Simulation Time
    request_id = 0
    for i in range(NUM_USERS):
        # Intialization of Event List
        start_time = sim_time + \
            get_random_variate(THINK_TIME_DIST["name"], THINK_TIME_DIST["params"])
        timeout = get_random_variate(TIMEOUT_DIST["name"], TIMEOUT_DIST["params"])
        service_time = get_random_variate(
            SERVICE_TIME_DIST["name"], SERVICE_TIME_DIST["params"])
        event_list.addEvent(event_type=EventType.create_request, start_time=start_time, event_attr={
                            "id": request_id, "timeout": timeout, "service_time": service_time})
        request_id += 1

    # Main loop for each run
    while request_id <= STOPPING_CRITERION:
        printLineBreak()
        event = event_list.getNextEvent()
        print(event)
        prev_sim_time = sim_time
        sim_time = event.start_time

        info_list.append(str("TIME" + "\t" + str(sim_time)))

        info_list.append(str("UTILIZATION" + "\t" + str(core_handler.getUtilization())))

        if event.event_type == EventType.create_request:
            request = Request(event.attr["id"],
                            event.attr["timeout"], event.attr["service_time"], event.start_time)
            print(str(sim_time), str(request), "Arrived", sep=" : ")
            response = thread_list.getThreadToRunOnCpu(request)
            if response == -1:
                queue_response = request_queue.addToQueue(request)
                if queue_response == -1:
                    print(str(sim_time), str(request), "Dropped", sep=" : ")
                
                    info_list.append(str(
                        "DROP" + "\t" + str(request.id) + "\t" + str(request.timestamp)))
            
                    # Adding a create Request event
                    start_time = sim_time + get_random_variate(THINK_TIME_DIST["name"], THINK_TIME_DIST["params"])
                    timeout = get_random_variate(TIMEOUT_DIST["name"], TIMEOUT_DIST["params"])
                    service_time = get_random_variate(SERVICE_TIME_DIST["name"], SERVICE_TIME_DIST["params"])
                    event_list.addEvent(event_type=EventType.create_request, start_time=start_time, event_attr={
                                    "id": request_id, "timeout": timeout, "service_time": service_time})
                    request_id += 1
            else:
                core_handler.getCore(response, thread_list, event_list, sim_time)
        
        elif event.event_type == EventType.departure:
            core_id = event.attr["core_id"]
            request = core_handler.cores[core_id].runningThread
            core_handler.cores[core_id].departure(thread_list, event_list, sim_time)
            print(str(sim_time), str(request), "Departed", sep=" : ")
            
            info_list.append(str("DEPART" + "\t" +
                                str(request.request.id) + "\t" + str(request.request.timestamp)))

            core_handler.allocatePendingThreads()
            request = request_queue.removeFromQueue()
            if not (request == -1):
                response = thread_list.getThreadToRunOnCpu(request)
                print(response)
                core_handler.getCore(response, thread_list, event_list, sim_time)

            # Adding a create Request event
            start_time = sim_time + get_random_variate(THINK_TIME_DIST["name"], THINK_TIME_DIST["params"])
            timeout = get_random_variate(TIMEOUT_DIST["name"], TIMEOUT_DIST["params"])
            service_time = get_random_variate(SERVICE_TIME_DIST["name"], SERVICE_TIME_DIST["params"])
            event_list.addEvent(event_type=EventType.create_request, start_time=start_time, event_attr={
                            "id": request_id, "timeout": timeout, "service_time": service_time})
            request_id += 1

        elif event.event_type == EventType.timeout:
            core_id = event.attr["core_id"]
            request = core_handler.cores[core_id].runningThread
            core_handler.cores[core_id].timeout(
                thread_list, event_list, sim_time)
            print(str(sim_time), str(request), "Timeout", sep=" : ")

            info_list.append(str("TIMEOUT" + "\t" +
                                str(request.request.id) + "\t" + str(request.request.timestamp)))

            core_handler.allocatePendingThreads()
            request = request_queue.removeFromQueue()
            if not (request == -1):
                response = thread_list.getThreadToRunOnCpu(request)
                core_handler.getCore(response, thread_list, event_list, sim_time)

            # Adding a create Request event
            start_time = sim_time + get_random_variate(THINK_TIME_DIST["name"], THINK_TIME_DIST["params"])
            timeout = get_random_variate(TIMEOUT_DIST["name"], TIMEOUT_DIST["params"])
            service_time = get_random_variate(SERVICE_TIME_DIST["name"], SERVICE_TIME_DIST["params"])
            event_list.addEvent(event_type=EventType.create_request, start_time=start_time, event_attr={
                            "id": request_id, "timeout": timeout, "service_time": service_time})
            request_id += 1

        elif event.event_type == EventType.end_quantum:
            core = core_handler.cores[event.attr["core_id"]]
            print(str(sim_time), str(core), str(core.runningThread), "Quantum End ", sep=" : ")
            if core.buffer.isEmpty():
                core.idle = True
                core.buffer.addJob(core.runningThread)
                core.checkBuffer(thread_list, event_list, sim_time)
            else:
                event_list.addEvent(event_type=EventType.switch_context, start_time=sim_time+CONTEXT_SWITCH_OVERHEAD, event_attr={"core_id": event.attr["core_id"]})

        elif event.event_type == EventType.switch_context:
            # Invariant is that buffer is not empty
            core = core_handler.cores[event.attr["core_id"]]
            print(str(sim_time), str(core), str(core.runningThread), "Context Switched ", sep=" : ")

            info_list.append(str("CONTEXT" + "\t" + str(core.id)))

            core.buffer.addJob(core.runningThread, "special")
            core.runningThread = None
            core.idle = True
            core.checkBuffer(thread_list, event_list, sim_time)

f = open("output.txt", "w+")
for item in info_list:
    f.write(item+"\n")
