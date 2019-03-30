class Request:
    """An abstraction for a Request"""

    def __init__(self, id, timeout, time_required, timestamp, time_spent_on_cpu):
        self.id = id
        self.timeout = timeout
        self.time_required = time_required
        self.timestamp = timestamp
        self.time_spent_on_cpu = time_spent_on_cpu


class Thread:
    """Abstraction for a Thread """

    def __init__(self, request, thread_id):
        self.request = request
        self.thread_id = thread_id
        self.running = False
        self.core_allocated = False


class ThreadList:
    """ An abstraction for the list of threds waiting to get into the core buffer """

    def __init__(self, max_threads, list_threads):
        self.max_threads = max_threads
        self.list_threads = list_threads
        self.available_threads = list(range(256))

    def isThreadAvailableForARequest():
        if(len(self.available_threads) == 0):
            return False
        else:
            return True

    def getThreadToRunOnCpu(request):
        if(isThreadAvailableForARequest()):
            thread_id = self.available_threads[0]
            del self.available_threads[0]
            thread = Thread(request, thread_id)
            self.list_threads.append(thread)
            return thread
        else:
            print "Calling without checking the status of Thread List"


class RequestQueue:
    """ An abstraction for the queue of Requests waiting to get a thread """

    def __init__(self, max_queue_length):
        self.max_queue_length = max_queue_length
        self.list_requests = []

    def addToQueue(request):
        if(len(self.list_requests) == max_queue_length):
            return DropRequest(request)
        else:
            self.list_requests.append(request)

    def removeFromQueue(request):
        self.list_requests.remove(request)

    def dropRequest(request):
        return -1
