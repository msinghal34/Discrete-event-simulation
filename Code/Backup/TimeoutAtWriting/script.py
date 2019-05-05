def script(info_list):
	drop_list = []				# List of number of drops in each run
	goodput_list = []			# List of number of goodputs in each run 
	timeout_list = []			# List of number of timeouts in each run
	context_switch_list = []	# List of Number of context switches in each run
	utilization_list = []		# List of list of util*time of each time difference in each run
	response_time_list = []		# List of list of response time of each request in each run
	time_list = [] 				# List of total time for each run including transient time
	num_users = []				# List of list of num_users*time of each time difference in each run

	previous_time = 0.0			# Previous time
	current_time = 0.0			# Current time

	for line in info_list:
		words = line.split()
		token = words[0]

		if token == "RUN":
			time_list.append(current_time)
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
			print("Wrong Token Found", token)

	del time_list[0]
	time_list.append(current_time)
	# Processing response_time & utilization
	response_time_list = [sum(item)/len(item) for item in response_time_list]
	utilization_list = [sum(x)/y for x, y in zip(utilization_list, time_list)]
	num_users = [sum(x)/y for x, y in zip(num_users, time_list)]
	
	print("Total time\t\t : ", time_list)

	print("Drop\t\t\t : ", drop_list)
	print("Goodput\t\t\t : ", goodput_list)
	print("Timeout\t\t\t : ", timeout_list)
	print("Context Switch\t\t : ", context_switch_list)

	print("Utilization\t\t : ", utilization_list)
	print("Response Time\t\t : ", response_time_list)
	print("Number of users\t\t : ", num_users)

	def mean(list_):
		return sum(list_)/len(list_)

	print("################### Averages ###################")
	print("Total time\t\t : ", mean(time_list))

	print("Drop\t\t\t : ", mean(drop_list))
	print("Goodput\t\t\t : ", mean(goodput_list))
	print("Timeout\t\t\t : ", mean(timeout_list))
	print("Context Switch\t\t : ", mean(context_switch_list))

	print("Utilization\t\t : ", mean(utilization_list))
	print("Response Time\t\t : ", mean(response_time_list))
	print("Number of users\t\t : ", mean(num_users))