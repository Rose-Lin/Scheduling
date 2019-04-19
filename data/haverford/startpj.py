import os
import sys
import subprocess
import shutil


if len(sys.argv) == 2 and sys.argv[-1] == "-h":
	print("Choices of <neighboring stucture>: \n NS1\t NS2\t NS3 \t NS4")
	print("For every 1000 iteration of simulated annealing, the program runs roughly 10 seconds.")
	exit(1)
elif len(sys.argv) != 3:
	print("Usage: " + 'python3 startpj.py' + "<# of iteration of simulated annealing> <neighboring structure>")
	print("Please type python3 startpj.py -h for help.")
	exit(1)

iterations = [sys.argv[1]]
NS_id = sys.argv[2]
if NS_id != "NS1" and NS_id != "NS2" and NS_id != "NS3" and NS_id !="NS4":
	print("Please give the correct neighboring structure. \n-h for more information.")
	exit(1)

constriant_file_name = "haverfordConstraints_major.txt"
studentpref_file_name = "haverfordStudentPrefs.txt" 
output_file_name = "output.txt"
semesterfile = "haverfordEnrollmentDataS14.csv"
cmd = "python3 get_haverford_info.py {} {} {}".format(semesterfile, studentpref_file_name, constriant_file_name)
subprocess.call(cmd)
prettyschedule_name = "prettyschedule.txt"
for iter in iterations:
	for i in range (1):
		cmd = "python3 scheduling.py {} {} {} {} {}".format(constriant_file_name, studentpref_file_name, output_file_name, iter, NS_id)
		prettyschedule = subprocess.check_output(cmd, shell= True)
		with open(prettyschedule_name, "wb") as file:
			file.write(prettyschedule)

