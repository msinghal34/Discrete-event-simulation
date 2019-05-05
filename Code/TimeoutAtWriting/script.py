def script(info_list, exclusion):
	# Excluding transient phase and only before the point of printing
	drop_list = []				# List of number of drops in each run
	goodput_list = []			# List of number of goodputs in each run 
	timeout_list = []			# List of number of timeouts in each run
	context_switch_list = []	# List of Number of context switches in each run
	utilization_list = []		# List of list of util*time of each time difference in each run
	response_time_list = []		# List of list of response time of each request in each run
	time_list = [] 				# List of time for each run
	num_users = []				# List of list of num_users*time of each time difference in each run

	transient_time = 0.0
	previous_time = 0.0
	current_time = 0.0

	index = -1
	def getNextLine():
		nonlocal index
		index += 1
		try:
			return info_list[index]
		except Exception as e:
			return "ERROR\tERROR"

	while True:
		line = getNextLine()
		words = line.split()
		token = words[0]

		if token == "RUN":
			time_list.append(current_time-transient_time)	# To account for previous run

			count = 0
			while count < exclusion:
				token = getNextLine().split()[0]
				if ((token == "TIMEOUT") or (token == "DEPART") or (token == "DROP")):
					count += 1
			words = getNextLine().split()
			token = words[0]
			assert token == "TIME"

			previous_time = float(words[1])
			current_time = float(words[1])
			transient_time = float(words[1])

			drop_list.append(0)
			goodput_list.append(0)
			timeout_list.append(0)
			context_switch_list.append(0)

			utilization_list.append([])
			num_users.append([])
			response_time_list.append([])

		elif token == "TIME":
			previous_time = current_time
			current_time = float(words[1])
			utilization_list[-1].append((current_time-previous_time)*float(words[2]))
			num_users[-1].append((current_time-previous_time)*float(words[3]))

		elif token == "CONTEXT":
			context_switch_list[-1] += 1

		elif token == "TIMEOUT":
			timeout_list[-1] += 1
			response_time_list[-1].append(current_time - float(words[2]))

		elif token == "DROP":
			drop_list[-1] += 1

		elif token == "DEPART":
			goodput_list[-1] += 1
			response_time_list[-1].append(current_time - float(words[2]))

		else:
			break

	del time_list[0]	# To remove dummy value
	time_list.append(current_time-transient_time)	# To account for last run

	# Processing lists
	response_time_list = [sum(item)/len(item) for item in response_time_list]
	utilization_list = [sum(x)/y for x, y in zip(utilization_list, time_list)]
	num_users = [sum(x)/y for x, y in zip(num_users, time_list)]

	context_switch_list = [x/(y+z) for x, y, z in zip(context_switch_list, goodput_list, timeout_list)]
	drop_list = [x/y for x, y in zip(drop_list, time_list)]
	goodput_list = [x/y for x, y in zip(goodput_list, time_list)]
	timeout_list = [x/y for x, y in zip(timeout_list, time_list)]
	throughput_list = [x+y for x, y in zip(goodput_list, timeout_list)]

	def mean(list_):
		return sum(list_)/len(list_)

	print("###################################### Statistics ######################################")
	print("Observation time\t\t\t : ", time_list)
	print("Avg. drop rate\t\t\t\t : ", drop_list)
	print("Avg. goodput\t\t\t\t : ", goodput_list)
	print("Avg. badput\t\t\t\t : ", timeout_list)
	print("Avg. throughput\t\t\t\t : ", throughput_list)
	print("Avg. no. of context switch per request\t : ", context_switch_list)
	print("Avg. utilization\t\t\t : ", utilization_list)
	print("Avg. response time\t\t\t : ", response_time_list)
	print("Avg. no. of users in system\t\t : ", num_users)

	print("###################################### Averages ######################################")
	print("Observation time\t\t\t : ", mean(time_list), "in ms")
	print("Avg. drop rate\t\t\t\t : ", mean(drop_list), "reqs per ms")
	print("Avg. goodput\t\t\t\t : ", mean(goodput_list), "reqs per ms")
	print("Avg. badput\t\t\t\t : ", mean(timeout_list), "reqs per ms")
	print("Avg. throughput\t\t\t\t : ", mean(throughput_list), "reqs per ms")
	print("Avg. no. of context switch per request\t : ", mean(context_switch_list), "switches per req")
	print("Avg. utilization\t\t\t : ", mean(utilization_list), "fraction")
	print("Avg. response time\t\t\t : ", mean(response_time_list), "in ms")
	print("Avg. no. of users in system\t\t : ", mean(num_users), "number")
	print("######################################################################################")
