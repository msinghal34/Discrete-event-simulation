class Request:
    """An abstraction for a Request"""

    def __init__(self, id, timeout, time_required, timestamp, time_spent_on_cpu=0, priority=0):
        self.id = id    # Request ID
        self.timeout = timeout  # Time to wait before timeout
        self.time_required = time_required  # Time required to complete this job
        self.timestamp = timestamp  # Timestamp when the request was created
        self.time_spent_on_cpu = time_spent_on_cpu  # Total time spent on cpu so far
        self.priority = priority    # Priority of this request

    def __repr__(self):
        return str("Request with id " + str(self.id))

class Thread:
    """Abstraction for a Thread """

    def __init__(self, request, id):
        self.request = request  # Which request is holding this thread
        self.id = id    # Thread ID
        self.running = False    # Whether this thread is currently running on a core
        # Has a core been allocated to this thread (it may be in buffer of a core)
        self.core_allocated = False

    def __repr__(self):
        return str("Thread: id " + str(self.id))

class ThreadList:
    """ An abstraction for the list of threads waiting to get into the core buffer """

    def __init__(self, max_threads):
        self.max_threads = max_threads  # Maximum number of threads in the list
        # List of threads which are currently in use by some request
        self.list_of_threads_in_use = []
        # Thread IDs available for new requests
        self.available_threads = list(range(max_threads))

    def isThreadAvailableForARequest(self):
        """
        Returns whether a thread is available for a new request
        """
        if (len(self.available_threads) == 0):
            return False
        else:
            return True

    def getThreadToRunOnCpu(self, request):
        """
        Returns and allocate a thread to a request if available
        """
        if (self.isThreadAvailableForARequest()):
            thread_id = self.available_threads[0]
            del self.available_threads[0]
            thread = Thread(request, thread_id)
            self.list_of_threads_in_use.append(thread)
            return thread
        else:
            print("No threads available")
            return -1

    def removeThread(self, thread_id):
        """
        Since, the request has been completed or timed out, It no longer needs a thread
        So it marks the thread corresponding to thread_id as available
        """
        for index, thread in enumerate(self.list_of_threads_in_use):
            if thread.id == thread_id:
                del self.list_of_threads_in_use[index]
                self.available_threads.append(thread_id)
                break

    def __repr__(self):
        return str("Thread List with number of threads " + str(self.max_threads))


class RequestQueue:
    """ An abstraction for the queue of Requests waiting to get a thread """

    def __init__(self, max_queue_length):
        # Maximum number of requests queue can hold
        self.max_queue_length = max_queue_length
        # List of requests currently residing in queue
        self.list_requests = []

    def addToQueue(self, request):
        """
        Add a new request to this queue (if there is space) else drop it
        """
        if (len(self.list_requests) == self.max_queue_length):
            print("Dropping Request with id : ", request.id)
            return -1
        else:
            self.list_requests.append(request)

    def removeFromQueue(self):
        """
        Remove the first request from the queue
        """
        if self.isEmpty():
            return -1
        request = self.list_requests[0]
        del self.list_requests[0]
        return request
    
    def isEmpty(self):
        """
        Returns whether request_queue is empty or not
        """
        return self.list_requests == []

    def __repr__(self):
        return str("Request Queue with max queue length " + str(self.max_queue_length))
