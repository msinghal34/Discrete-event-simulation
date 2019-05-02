import heapq


class PriorityQueue:
    """
    A priority queue specialized for event list
    """

    def __init__(self):
        self.heap = []
        heapq.heapify(self.heap)

    def __str__(self):
        return ' '.join([str(i) for i in self.heap])

    def isEmpty(self):
        return len(self.heap) == 0

    def push(self, event):
        heapq.heappush(self.heap, [event.start_time, event])

    def pop(self):
        [_, event] = heapq.heappop(self.heap)
        return event

    def len(self):
        return len(self.heap)


def printLineBreak():
    print("-------------------------------------------------------------------"*2)