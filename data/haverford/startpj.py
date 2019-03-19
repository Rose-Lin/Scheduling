import os
import subprocess
import shutil

iterations = ["100", "500", "1000", "2000", "3000", "4000", "5000","6000"]
constriant_file_name = "haverfordConstraints_major.txt"
studentpref_file_name = "haverfordStudentPrefs.txt" 
output_file_name = "output.txt"
prettyschedule_name = "prettyschedule-result.txt"
# cmd = "python3 get_bmc_info.py data/{} {} {}".format(semesterfile, studentpref_file_name, constriant_file_name)
# subprocess.call(cmd)
for iter in iterations:
    cmd = "python3 scheduling.py {} {} {} {}".format(constriant_file_name, studentpref_file_name, output_file_name, iter)
    prettyschedule = subprocess.check_output(cmd, shell= True)
    # print(prettyschedule)
    with open(prettyschedule_name, "ab") as file:
        file.write(prettyschedule)
    # cmd = "{} &> {} ".format(prettyschedule, prettyschedule_name)
    # subprocess.call(cmd)

