from thread import *
from event import *

CURRENT_TIME = 0
QUANTUM_SIZE = 5


class Buffer:
    """
    An abstraction of the buffer of a core
    It stores a list of jobs and it has a specified maximum capacity
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer_list = []

    def getNextJob(self, policy):
        """
        Return a job from the buffer according to the given policy
        """
        if self.buffer_list == []:
            return -1
        return policy(self.buffer_list)

    def isFull(self):
        return self.capacity == len(self.buffer_list)

    def addJob(self, job):
        """
        Add a job to the buffer
        """
        if self.isFull():
            return -1
        self.buffer_list.append(job)
        return 1

    def __str__(self):
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

    def __init__(self, id, buffer, policy):
        self.id = id
        self.buffer = buffer
        self.policy = policy
        self.idle = True
        self.runningThread = None

    def isIdle(self):
        return self.idle

    def departure(self):
        """
        The request is completed and should be counted towards goodput
        """
        THREAD_LIST.removeThread(self.runningThread.thread_id)
        self.runningThread = None
        next_job = self.buffer.getNextJob(self.policy)
        if next_job == -1:  # Empty Buffer
            self.idle = True
        else:
            self.runningThread = next_job
            if next_job.request.timeout + next_job.request.timestamp > CURRENT_TIME:
                self.timeout()
            else:
                next_job.running = True
                self.runningThread = next_job
                EVENT_LIST.addEvent(
                    EventType.end_quantum, CURRENT_TIME+QUANTUM_SIZE, {'core_id': self.id})

    def timeout(self):
        """
        The request has timed out and should be counted towards badput
        """
        THREAD_LIST.removeThread(self.runningThread.thread_id)
        self.runningThread = None
        next_job = self.buffer.getNextJob(self.policy)
        if next_job == -1:  # Empty Buffer
            self.idle = True
        else:
            if next_job.request.timeout + next_job.request.timestamp > CURRENT_TIME:
                self.timeout()
            else:
                next_job.running = True
                self.runningThread = next_job
                EVENT_LIST.addEvent(
                    EventType.end_quantum, CURRENT_TIME+QUANTUM_SIZE, {'core_id': self.id})

    def __str__(self):
        """
        Debugging Purpose Only
        Prints the state of a core
        """
        repr = str("Core: " + "ID : " + str(self.id) + "Policy: " + str(self.policy))
        repr += str(self.buffer)
        return repr


class CoreHandler:
    """
    An abstraction of OS which decides which core to assign to a particular thread
    """

    def __init__(self, cores):
        self.cores = cores

    def getCore(self):
        for core in self.cores:
            if (core.buffer.isFull() == False):
                return core     # Found a core
        return -1   # No cores are empty

    def __str__(self):
        """
        Debugging Purpose Only
        Prints the state of core handler
        """
        repr = str("Core Handler : " + " Num of Cores : " +
                   str(len(self.cores)))
        for core in self.cores:
            repr += str(core)
        return repr
