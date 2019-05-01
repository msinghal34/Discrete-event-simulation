def fcfs(buffer_list):
    """
    First come First Serve Policy
    """
    if(len(buffer_list) > 0):
        temp = buffer_list[0]
        del buffer_list[0]
        return temp
    else:
        return -1


def roundRobin(buffer_list):
    """
    Round Robin Policy
    """
    if(len(buffer_list) > 0):
        temp = buffer_list[0]
        del buffer_list[0]
        return temp
    else:
        return -1


def priority(buffer_list):
    """
    Policy returns the request with maximum priority
    """
    if(len(buffer_list) > 0):
        max_p = -1
        index = -1
        for i in range(buffer_list):
            if(buffer_list[i].request.priority > max_p):
                index = i
                max_p = buffer_list[i].request.priority

        temp = buffer_list[index]
        del buffer_list[index]
        return temp
    else:
        return -1
