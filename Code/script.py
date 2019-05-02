import os
import sys

response_time_list = []
goodput_list = []
badput_list = []
drop_list = []
utilization_list = []
timeout_list = []
context_switch_list = []
num_requests = []

previous_time = 0.0
current_time = 0.0
time_relax = 0.0

f = open("output.txt", 'r')
for line in f:
	words = line.split()
	token = words[0]

	if token == "RUN":
		response_time_list.append([])
		num_requests.append(0)
		goodput_list.append(0)
		badput_list.append(0)
		drop_list.append(0)
		context_switch_list.append(0)
		timeout_list.append(0)
		utilization_list.append([0.0, 0.0])
		# Exclude transient phase
		for i in range(750):
			f.readline()
		time_checker = f.readline().split()
		while time_checker[0] != "TIME":
			time_checker = f.readline().split()
		# Now time token found
		previous_time = 0.0
		current_time = 0.0
		time_relax = float(time_checker[1])

	elif token == "TIME":
		previous_time = current_time
		current_time = float(words[1]) - time_relax

	elif token == "UTILIZATION":
		assert previous_time == utilization_list[-1][0]
		if current_time != 0:
			utilization_list[-1][1] = (utilization_list[-1][0]*utilization_list[-1][1] + (current_time-previous_time)*float(words[1]))/current_time
			utilization_list[-1][0] = current_time

	elif token == "CONTEXT":
		context_switch_list[-1] = context_switch_list[-1]+1

	elif token == "TIMEOUT":
		num_requests[-1] += 1
		timeout_list[-1] = timeout_list[-1]+1
		badput_list[-1] = badput_list[-1]+1

	elif token == "DROP":
		num_requests[-1] += 1
		drop_list[-1] = drop_list[-1]+1

	elif token == "DEPART":
		num_requests[-1] += 1
		goodput_list[-1] = goodput_list[-1]+1
		response_time_list[-1].append(current_time+time_relax - float(words[2]))

	else:
		print("Wrong Token Found", token)

response_time_list = [sum(item)/len(item) for item in response_time_list]
utilization_list = [item[1] for item in utilization_list]

print("Response Time", response_time_list)
print("Utilization", utilization_list)

goodput_list = [x/y for x, y in zip(goodput_list, num_requests)]
badput_list = [x/y for x, y in zip(badput_list, num_requests)]
drop_list = [x/y for x, y in zip(drop_list, num_requests)]
timeout_list = [x/y for x, y in zip(timeout_list, num_requests)]
context_switch_list = [x/y for x, y in zip(context_switch_list, num_requests)]

print("Goodput", goodput_list)
print("Badput", badput_list)
print("Drop", drop_list)
print("Timeout", timeout_list)
print("Context Switch", context_switch_list)