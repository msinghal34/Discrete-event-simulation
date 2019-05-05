import sys
import os
import yaml
import time

from event import Event, EventList, EventType
from distribution import get_random_variate
from server import *
from thread import Request, Thread, ThreadList, RequestQueue
from script import *

t = time.time()
with open("config.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
    	print("Error 0")

NUM_RUNS = config["num_runs"]       # Number of runs
NUM_CORES = config["num_cores"]     # Number of cores
NUM_THREADS = config["num_threads"]    # Number of threads in the system
# Max length of the Request queue
MAX_REQUEST_QUEUE_LENGTH = config["max_request_queue_length"]
POLICY = config["policy"]   # Scheduling policy for picking requests from buffer
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

# Main loop to process events until the number of requests generated exceeds stopping criterion
for z in range(NUM_RUNS):
    info_list.append(str("RUN\t" + str(z)))   
    # Init of each run
    cores = []  # Cores in the system
    for i in range(NUM_CORES):
        cores.append(Core(i, Buffer(i), POLICY, QUANTUM_SIZE))
    core_handler = CoreHandler(cores)    # Core Handler Instance

    event_list = EventList()    # An instance of the event list
    thread_list = ThreadList(NUM_THREADS)    # A Thread List instance
    # An instance of Request queue
    request_queue = RequestQueue(MAX_REQUEST_QUEUE_LENGTH)

    sim_time = 0.0  # Current Simulation Time
    request_id = 0
    num_serviced = 0    # NUmber of requests dropped or timed out or departed
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
    while num_serviced < STOPPING_CRITERION:
        event = event_list.getNextEvent()
        prev_sim_time = sim_time
        sim_time = event.start_time
        info_list.append(str("TIME" + "\t" + str(sim_time) + "\t" + str(core_handler.getUtilization()) + "\t" + str(len(thread_list.list_of_threads_in_use) + len(request_queue.list_requests))))
        if event.event_type == EventType.create_request:
            request = Request(event.attr["id"],
                            event.attr["timeout"], event.attr["service_time"], event.start_time)

            response = thread_list.getThreadToRunOnCpu(request)
            if response == -1:
                queue_response = request_queue.addToQueue(request)
                if queue_response == -1:
                    num_serviced += 1

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
                # Providing space in core buffer to this request (which got thread)
                core_handler.getCore(response, thread_list, event_list, sim_time)
        
        elif event.event_type == EventType.departure:
            num_serviced += 1
            core_id = event.attr["core_id"]
            request = core_handler.cores[core_id].runningThread
            core_handler.cores[core_id].departure(thread_list, event_list, sim_time)
            if request.request.timeout + request.request.timestamp < sim_time:  # Time out request
                info_list.append(str("TIMEOUT" + "\t" + str(request.request.id) + "\t" + str(request.request.timestamp)))
            else:
                info_list.append(str("DEPART" + "\t" + str(request.request.id) + "\t" + str(request.request.timestamp)))
                
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

            if core.buffer.isEmpty():
                core.idle = True
                core.buffer.addJob(core.runningThread)
                core.checkBuffer(thread_list, event_list, sim_time)
            else:
                event_list.addEvent(event_type=EventType.switch_context, start_time=sim_time+CONTEXT_SWITCH_OVERHEAD, event_attr={"core_id": event.attr["core_id"]})

        elif event.event_type == EventType.switch_context:
            # Invariant is that buffer is not empty
            core = core_handler.cores[event.attr["core_id"]]

            info_list.append(str("CONTEXT" + "\t" + str(core.id)))
            core.buffer.addJob(core.runningThread)
            core.runningThread = None
            core.idle = True
            core.checkBuffer(thread_list, event_list, sim_time)

if len(sys.argv) == 2:
    if sys.argv[1] == "1":
        # If log file is needed
        f = open("output.log", 'w+')
        for item in info_list:
        	f.write(item + "\n")

print("Main time", time.time()-t)
t = time.time()
script(info_list, STOPPING_CRITERION/2)
print("Script time", time.time()-t)