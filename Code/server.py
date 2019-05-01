from event import EventType


class Buffer:
    """
    An abstraction of the buffer of a core
    It stores a list of jobs and it has a specified maximum capacity
    """

    def __init__(self, capacity):
        self.capacity = capacity    # Maximum number of threads that buffer can hold
        self.buffer_list = []       # List of threads currently in buffer

    def getNextJob(self, policy):
        """
        Return a job from the buffer according to the given policy
        """
        if self.buffer_list == []:
            return -1
        return policy(self.buffer_list)

    def isFull(self):
        """
        Returns whether the buffer is full or not
        """
        return self.capacity == len(self.buffer_list)

    def addJob(self, job):
        """
        Add a job to the buffer
        """
        if self.isFull():
            return -1
        self.buffer_list.append(job)
        return 1

    def __repr__(self):
        """
        For Debugging Purpose Only
        Prints the state of buffer
        """
        repr = str("Buffer: " + "Capacity : " + str(self.capacity))
        for job in self.buffer_list:
            repr += str(job)
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

    def departure(self, thread_list, event_list, sim_time, quantum_size):
        """
        The request is completed and should be counted towards goodput
        """
        thread_list.removeThread(self.runningThread.thread_id)
        self.runningThread = None
        next_job = self.buffer.getNextJob(self.policy)
        if next_job == -1:  # Empty Buffer
            self.idle = True
        else:
            self.runningThread = next_job
            if next_job.request.timeout + next_job.request.timestamp > sim_time:
                self.timeout(thread_list, event_list, sim_time, quantum_size)
            else:
                next_job.running = True
                self.runningThread = next_job
                event_list.addEvent(
                    EventType.end_quantum, sim_time+quantum_size, {'core_id': self.id})

    def timeout(self, thread_list, event_list, sim_time, quantum_size):
        """
        The request has timed out and should be counted towards badput
        """
        thread_list.removeThread(self.runningThread.thread_id)
        self.runningThread = None
        next_job = self.buffer.getNextJob(self.policy)
        if next_job == -1:  # Empty Buffer
            self.idle = True
        else:
            if next_job.request.timeout + next_job.request.timestamp > sim_time:
                self.timeout(thread_list, event_list, sim_time, quantum_size)
            else:
                next_job.running = True
                self.runningThread = next_job
                event_list.addEvent(
                    EventType.end_quantum, sim_time+quantum_size, {'core_id': self.id})

    def __repr__(self):
        """
        Debugging Purpose Only
        Prints the state of a core
        """
        repr = str("Core: " + "ID : " + str(self.id) +
                   "Policy: " + str(self.policy) + "Quantum Size: " + str(self.quantum_size))
        repr += str(self.buffer)
        return repr


class CoreHandler:
    """
    An abstraction of OS which decides which core to assign to a particular thread
    """

    def __init__(self, cores):
        self.cores = cores      # List of cores in the system which it will be handling

    def getCore(self):
        """
        It returns a core (if available) for a thread
        """
        for core in self.cores:
            if (core.buffer.isFull() == False):
                return core     # Found a core
        return -1   # No cores are empty

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
