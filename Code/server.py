from event import EventType

class Buffer:
    """
    An abstraction of the buffer of a core
    It stores a list of jobs
    """

    def __init__(self, id):
        self.id = id
        self.buffer_list = []       # List of threads currently in buffer

    def getNextJob(self):
        """
        Return the first job from the buffer
        """
        if self.buffer_list == []:
            return -1
        else:
            temp = self.buffer_list[0]
            del self.buffer_list[0]
            return temp

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
        self.buffer_list.append(job)
        return 1
    
    def __repr__(self):
        """
        For Debugging Purpose Only
        Prints the state of buffer
        """

        repr = str("Buffer: buffer_list ")
        for job in self.buffer_list:
            repr += str(job.id) + " "
        if self.buffer_list == []:
            repr += "empty"
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
        if self.idle == False:
            print("Error : Server should have been idle")
        else:
            job = self.buffer.getNextJob()
            if job == -1:
                print(str(self) + " says Buffer is empty")
            else:   # Found a job to schedule
                if job.request.timeout + job.request.timestamp < sim_time + self.quantum_size:  # Add timeout event
                    self.idle = False   # For the purpose of timeout functionality, it is false
                    self.runningThread = job    # But it won't run on CPU since start_time is sim_time
                    event_list.addEvent(event_type=EventType.timeout, start_time=sim_time, event_attr={"core_id": self.id})
                else:   # If buffer is not empty and policy is roundRobin, add end quantum
                    if self.policy == "roundRobin":
                        self.idle = False
                        self.runningThread = job
                        if (job.request.time_required - job.request.time_spent_on_cpu <= self.quantum_size):    # Add departure event
                            start_time = sim_time + job.request.time_required - job.request.time_spent_on_cpu
                            event_list.addEvent(event_type=EventType.departure,start_time = start_time, event_attr={"core_id": self.id})
                        else:   # Add end quantum event
                            start_time = sim_time + self.quantum_size
                            job.request.time_spent_on_cpu += self.quantum_size
                            event_list.addEvent(event_type=EventType.end_quantum, start_time=start_time, event_attr={"core_id": self.id})
                    elif self.policy == "fcfs":     # Add departure event
                        self.idle = False
                        self.runningThread = job
                        start_time = sim_time + self.runningThread.request.time_required
                        event_list.addEvent(event_type=EventType.departure, start_time=start_time, event_attr={"core_id": self.id})

    def departure(self, thread_list, event_list, sim_time):
        """
        The request is completed and should be departed
        """
        self.runningThread.request.time_spent_on_cpu = self.runningThread.request.time_required
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
        return str("Core: " + "id " + str(self.id))


class CoreHandler:
    """
    An abstraction of OS which decides which core to assign to a particular thread
    """

    def __init__(self, cores):
        self.cores = cores      # List of cores in the system which it will be handling

    def getCore(self, thread, thread_list, event_list, sim_time):
        """
        It adds the thread to run on a core with lowest load
        """
        load = []
        for core in self.cores:
            load.append(core.buffer.getBufferLength() + int(not core.isIdle()))
        core = self.cores[load.index(min(load))]
        print("CoreHandler: added", str(thread), "to", str(core))
        core.buffer.addJob(thread)
        if core.isIdle():
            core.checkBuffer(thread_list, event_list, sim_time)
    
    def getUtilization(self):
        count = 0.0
        for core in self.cores:
            count += int(not core.isIdle())
        return count/len(self.cores)

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