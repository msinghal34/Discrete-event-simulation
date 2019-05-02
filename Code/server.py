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

    def checkBuffer(self, thread_list, event_list, sim_time):
        """
        Assumption: server is idle
        """
        if self.isIdle() == False:
            print("Error : Server should have been idle")
        else:
            job = self.buffer.getNextJob()
            if job == -1:
                print("Buffer is empty")
            else:
                # Found a job to schedule
                if job.request.timeout + job.request.timestamp < sim_time + self.quantum_size:
                    # Request has timed out
                    self.timeout(thread_list, event_list, sim_time)
                else:
                    # If buffer is not empty and policy is add end quantum
                    if self.policy == "roundRobin":
                        if not self.buffer.isEmpty:
                            event_list.addEvent()
                            

    def departure(self, thread_list, event_list, sim_time):
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
                self.timeout(thread_list, event_list, sim_time, self.quantum_size)
            else:
                next_job.running = True
                self.runningThread = next_job
                event_list.addEvent(
                    EventType.end_quantum, sim_time+self.quantum_size, {'core_id': self.id})

    def timeout(self, thread_list, event_list, sim_time):
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
                self.timeout(thread_list, event_list, sim_time, self.quantum_size)
            else:
                next_job.running = True
                self.runningThread = next_job
                event_list.addEvent(
                    EventType.end_quantum, sim_time+self.quantum_size, {'core_id': self.id})

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
        self.pending_threads = []   # List of threads pending to get a core

    def getCore(self, thread):
        """
        It adds the thread to run on a core if its buffer has space otherwise append the thread to pending_threads
        """
        load = []
        for core in self.cores:
            load.append(core.buffer.getBufferLength())
        core = self.cores[load.index(min(load))]
        if core.buffer.addJob(self.pending_threads[0]) == -1:
            self.pending_threads.append(thread)
        else:
            if core.isIdle():
                core.checkBuffer()

    def allocatePendingThreads(self):
        """
        Called from departure and timeout functions
        Check all the cores for any empty space in the cores
        """
        load = []
        for core in self.cores:
            load.append(core.buffer.getBufferLength())
        core = self.cores[load.index(min(load))]
        if core.buffer.addJob(self.pending_threads[0]) == -1:
            print("Error : allocatePendingThreads should have been called only after departure or timeout")
        else:
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
