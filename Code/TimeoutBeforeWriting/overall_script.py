import os
import matplotlib.pyplot as plt 
import statistics

users = [500, 750, 1000, 1250, 1500, 1650, 1800, 2000, 2100, 2200, 2300, 2400, 2500, 2600, 3000]

result_file = "results.txt"
os.system("> " + result_file)
for user in users:
	print("For Number of users = " + str(user) + ":")
	os.system(str("python3 main.py " + str(user) + " " + str(result_file)))

f = open(result_file, "r")

avg_resp = []
std_resp = []
avg_util = []
avg_cs = []
avg_good = []
avg_bad = []
avg_drop = []
avg_through = []

for line in f.readlines():
	t = line.split()
	avg_resp.append(float(t[0]))
	std_resp.append(float(t[1]))
	avg_util.append(float(t[2]))
	avg_cs.append(float(t[3]))
	avg_good.append(float(t[4]))
	avg_bad.append(float(t[5]))
	avg_through.append(float(t[6]))
	avg_drop.append(float(t[7]))

# now do the plotting
std_resp = [x * 2 for x in std_resp] ## basically 95.47 % of the data is within 2 std deviation
plt.plot(users, avg_resp, marker='o', color='b')
plt.xlabel('Number of Users') 
plt.ylabel('95% Confidence interval of average response time (in ms)')  
plt.title('Average Response Time vs Number of Users') 
plt.errorbar(users, avg_resp, yerr=std_resp)
plt.savefig('Results/Response Time.png')
plt.close()
###

plt.plot(users, avg_util, marker='o', color='b')
plt.xlabel('Number of Users')
plt.ylabel('Average Utilisation (fraction)')
plt.title('Average Utilisation vs Number of Users')
plt.savefig('Results/Utilisation.png')
plt.close()
# ###

plt.plot(users, avg_cs, marker='o', color='b')
plt.xlabel('Number of Users')
plt.ylabel('Avg. no. of context switch per request (switches per request)')
plt.title('Avg. no. of context switch per request vs Number of Users')
plt.savefig('Results/Context Switch.png')
plt.close()
# ###

plt.plot(users, avg_good, marker='o', color='b')
plt.xlabel('Number of Users')
plt.ylabel('Average Goodput (reqs per ms)')
plt.title('Average Goodput vs  Number of Users')
plt.savefig('Results/Goodput.png')
plt.close()
# ##

plt.plot(users, avg_bad, marker='o', color='b')
plt.xlabel('Number of Users')
plt.ylabel('Average Badput (reqs per ms)')
plt.title('Average Badput vs Number of Users')
plt.savefig('Results/Badput.png')
plt.close()
# ##

plt.plot(users, avg_through, marker='o', color='b')
plt.xlabel('Number of Users')
plt.ylabel('Average Throughput (reqs per ms)')
plt.title('Average Throughput vs Number of Users')
plt.savefig('Results/Throughput.png')
plt.close()

# ##

plt.plot(users, avg_drop, marker='o', color='b')
plt.xlabel('Number of Users')
plt.ylabel('Average drop rate (reqs per ms)')
plt.title('Average drop rate vs Number of Users')
plt.savefig('Results/Drop Rate.png')
plt.close()