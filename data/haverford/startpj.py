import os
import subprocess
import shutil
# import scheduling

iterations = ["500", "1000","1500","2000", "2500",  "3000","3500", "4000","4500", "5000"]
# iterations = ["2500"]
constriant_file_name = "haverfordConstraints_major.txt"
studentpref_file_name = "haverfordStudentPrefs.txt" 
output_file_name = "output.txt"
# prettyschedule_name = "prettyschedule-result2.txt"
# prettyschedule_name = "a.txt"
# prettyschedule_name = "NS2.txt"
prettyschedule_name = "NS1.txt"
# prettyschedule_name = "conflict_pair.txt"
# prettyschedule_name = "NS3.txt"
# cmd = "python3 get_bmc_info.py data/{} {} {}".format(semesterfile, studentpref_file_name, constriant_file_name)
# subprocess.call(cmd)
for iter in iterations:
	for i in range (10):
		cmd = "python3 scheduling.py {} {} {} {}".format(constriant_file_name, studentpref_file_name, output_file_name, iter)
		prettyschedule = subprocess.check_output(cmd, shell= True)
		with open(prettyschedule_name, "ab") as file:
			file.write(prettyschedule)

