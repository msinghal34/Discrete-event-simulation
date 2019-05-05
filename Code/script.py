import os
import sys

drop_list = []				# List of number of drops in each run
goodput_list = []			# List of number of goodputs in each run 
timeout_list = []			# List of number of timeouts in each run
context_switch_list = []	# List of Number of context switches in each run
utilization_list = []		# List of list of util*time of each time difference in each run
response_time_list = []		# List of list of response time of each request in each run
transient_time_list = []	# List of transient time for each run
time_list = [] 				# List of total time for each run including transient time

exclusion = 10 				# Number of lines to exclude

previous_time = 0.0			# Previous time including transient time
current_time = 0.0			# Current time including transient time
transient_time = 0.0		# Transient time to exclude 

f = open("output.txt", 'r')
for line in f:
	words = line.split()
	token = words[0]

	if token == "RUN":
		time_list.append(current_time)
		drop_list.append(0)
		goodput_list.append(0)
		timeout_list.append(0)
		context_switch_list.append(0)

		utilization_list.append([])
		response_time_list.append([])
		for i in range(exclusion):	# Exclude transient phase
			f.readline()
		temp_token = f.readline().split()
		while temp_token[0] != "TIME":	# Untill time token is found
			temp_token = f.readline().split()
		
		transient_time = float(temp_token[1])
		transient_time_list.append(transient_time)
		previous_time = transient_time
		current_time = transient_time
		# Now metrics starts accumulating

	elif token == "TIME":
		previous_time = current_time
		current_time = float(words[1])
		utilization_list[-1].append((current_time-previous_time)*float(words[2]))

	elif token == "CONTEXT":
		context_switch_list[-1] += 1

	elif token == "TIMEOUT":
		timeout_list[-1] += 1

	elif token == "DROP":
		drop_list[-1] += 1

	elif token == "DEPART":
		goodput_list[-1] += 1
		response_time_list[-1].append(current_time - float(words[2]))

	else:
		print("Wrong Token Found", token)

del time_list[0]
# Processing response_time & utilization
response_time_list = [sum(item)/len(item) for item in response_time_list]
utilization_list = [sum(item)/(current_time-transient_time) for item in utilization_list]

print("Transient time\t\t : ", transient_time_list)
print("Total time\t\t : ", time_list)

print("Drop\t\t\t : ", drop_list)
print("Goodput\t\t\t : ", goodput_list)
print("Timeout\t\t\t : ", timeout_list)
print("Context Switch\t\t : ", context_switch_list)

print("Utilization\t\t : ", utilization_list)
print("Response Time\t\t : ", response_time_list)
