from event import EventType
from policy import *

class Buffer:
    """
    An abstraction of the buffer of a core
    It stores a list of jobs and it has a specified maximum capacity
    """

    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity    # Maximum number of threads that buffer can hold
        self.buffer_list = []       # List of threads currently in buffer
        self.policy_dict = {
            "fcfs": fcfs,
            "roundRobin": roundRobin,
            "priority": priority,
        }

    def getNextJob(self, policy):
        """
        Return a job from the buffer according to the given policy
        """
        if self.buffer_list == []:
            return -1
        return self.policy_dict[policy](self.buffer_list)

    def isFull(self):
        """
        Returns whether the buffer is full or not
        """
        return self.capacity == len(self.buffer_list)
    
    def getBufferLength(self):
        """
        Returns the length of the buffer list
        """
        return len(self.buffer_list)

    def isEmpty(self):
        """
        Checks whether buffer is empty or not
        """
        return len(self.buffer_list) == 0
    
    def addJob(self, job):
        """
        Add a job to the buffer
        """
        print(str(self), " -> addJob()")
        if self.isFull():
            return -1
        self.buffer_list.append(job)
        return 1

    def __repr__(self):
        """
        For Debugging Purpose Only
        Prints the state of buffer
        """

        repr = str("Buffer: Capacity " + str(self.capacity) + ", buffer_list ")
        for job in self.buffer_list:
            repr += str(job.id) + " "
        if self.buffer_list == []:
            repr += "Empty"
        return repr


class Core:
    """
    An abstraction of a core of a CPU
    """

    def __init__(self, id, buffer, policy, quantum_size):
        self.id = id                        # Core ID
        self.buffer = buffer                # Buffer associated with the core
        self.policy = policy                # Policy for scheduling jobs
        self.idle = True                    # Is core idle
        self.runningThread = None           # Thread (if running) on this core
        self.quantum_size = quantum_size    # Quantum Size for which to run a job

    def isIdle(self):
        """
        Returnd whether the core is idle
        """
        return self.idle

    def checkBuffer(self, thread_list, event_list, sim_time):
        """
        Assumption: server is idle
        Use: Server is idle, is there something in buffer to utilize CPU   
        """
        if self.isIdle() == False:
            print("Error : Server should have been idle")
        else:
            job = self.buffer.getNextJob(self.policy)
            if job == -1:
                print(str(self) + " says Buffer is empty")
            else:
                # Found a job to schedule
                if job.request.timeout + job.request.timestamp < sim_time + self.quantum_size:
                    # Request has timed out
                    self.idle = False
                    self.runningThread = job
                    event_list.addEvent(event_type=EventType.timeout, start_time=sim_time, event_attr={"core_id": self.id})
                else:
                    # If buffer is not empty and policy is roundRobin, add end quantum
                    if self.policy == "roundRobin":
                        # TODO
                        self.idle = False
                        job.request.time_spent_on_cpu += self.quantum_size
                        self.runningThread = job
                        if not self.buffer.isEmpty:
                            event_list.addEvent(event_type=EventType.end_quantum, start_time=sim_time, event_attr={"core_id": self.id})
                    elif self.policy == "fcfs":
                        self.idle = False
                        self.runningThread = job
                        start_time = sim_time + self.runningThread.request.time_required
                        event_list.addEvent(event_type=EventType.departure, start_time=start_time, event_attr={"core_id": self.id})

    def departure(self, thread_list, event_list, sim_time):
        """
        The request is completed and should be departed
        """
        if self.policy == "fcfs":
            self.runningThread.request.time_spent_on_cpu = self.runningThread.request.time_required
        elif self.policy == "roundRobin":
            print("round robin is todo")    # TODO
        thread_list.removeThread(self.runningThread.id)
        self.idle = True
        self.runningThread = None
        self.checkBuffer(thread_list, event_list, sim_time)

    def timeout(self, thread_list, event_list, sim_time):
        """
        Only called by checkBuffer if the job has timed out
        The request has timed out and should be counted towards badput
        """
        thread_list.removeThread(self.runningThread.id)
        self.idle = True
        self.runningThread = None
        self.checkBuffer(thread_list, event_list, sim_time)

    def __repr__(self):
        """
        Debugging Purpose Only
        Prints the state of a core
        """
        repr = str("Core: " + "id " + str(self.id) +
                   ", Policy " + str(self.policy) + ", Quantum Size " + str(self.quantum_size))
        repr += str(self.buffer)
        return repr


class CoreHandler:
    """
    An abstraction of OS which decides which core to assign to a particular thread
    """

    def __init__(self, cores):
        self.cores = cores      # List of cores in the system which it will be handling
        self.pending_threads = []   # List of threads pending to get a core

    def getCore(self, thread, thread_list, event_list, sim_time):
        """
        It adds the thread to run on a core if its buffer has space otherwise append the thread to pending_threads
        """
        print("CoreHandler -> getCore()")
        load = []
        for core in self.cores:
            load.append(core.buffer.getBufferLength() + int(not core.isIdle()))
        print("Load " , load)
        core = self.cores[load.index(min(load))]
        if core.buffer.addJob(thread) == -1:
            print("CoreHandler: added", str(thread), "to pending_threads")
            self.pending_threads.append(thread)
        else:
            if core.isIdle():
                core.checkBuffer(thread_list, event_list, sim_time)

    def allocatePendingThreads(self):
        """
        Called from departure and timeout functions
        Check all the cores for any empty space in the cores
        """
        if not (self.pending_threads == []):
            load = []
            for core in self.cores:
                load.append(core.buffer.getBufferLength())
            core = self.cores[load.index(min(load))]
            if core.buffer.addJob(self.pending_threads[0]) == -1:
                print("Error : allocatePendingThreads should have been called only after departure or timeout")
            else:
                thread = self.pending_threads[0]
                print("CoreHandler: removed", str(thread), "from pending_thread")
                del self.pending_threads[0]
                if core.isIdle():
                    core.checkBuffer()
    
    def __repr__(self):
        """
        Debugging Purpose Only
        Prints the state of core handler
        """
        repr = str("Core Handler : " + " Num of Cores : " +
                   str(len(self.cores)))
        for core in self.cores:
            repr += str(core)
        return repr
