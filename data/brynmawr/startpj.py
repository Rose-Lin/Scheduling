import os
import subprocess

semesterdata = os.listdir("./data")
try:
    os.mkdir("studentpreference")
except(FileExistsError):
    print("dir \'studentpreference\' already exists")

try:
    os.mkdir("constraints")
except(FileExistsError):
    print("dir \'constraints\' already exists")

try:
    os.mkdir("outputschedule")
except(FileExistsError):
    print("dir \'outputschedule\' already exists")

try:
    os.mkdir("prettyschedule")
except(FileExistsError):
    print("dir \'prettyschedule\' already exists")


for semesterfile in semesterdata: 
    semester =  semesterfile[:-4].lower()
    constriant_file_name = "./constraints/bmcconstraints-" + semester + ".txt"
    studentpref_file_name = "./studentpreference/bmcstudentpref-" + semester + ".txt"
    output_file_name = "./outputschedule/output-" + semester + ".txt"
    prettyschedule_name = "./prettyschedule/prettyschedule-" + semester + ".txt"
    cmd = "python3 get_bmc_info.py data/{} {} {}".format(semesterfile, studentpref_file_name, constriant_file_name)
    subprocess.call(cmd)
    cmd = "python3 scheduling.py {} {} {}".format(constriant_file_name, studentpref_file_name, output_file_name)
    prettyschedule = subprocess.check_output(cmd, shell= True)
    # print(prettyschedule)
    with open(prettyschedule_name, "wb") as file:
        file.write(prettyschedule)
    # cmd = "{} &> {} ".format(prettyschedule, prettyschedule_name)
    # subprocess.call(cmd)

