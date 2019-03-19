import os
import subprocess
import shutil

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
    shutil.rmtree("prettyschedule")
    os.mkdir("prettyschedule")
    print("dir \'prettyschedule\' removed")

iterations = ["100", "500", "1000", "2000", "3000", "4000", "5000", "6000", "7000"]
for semesterfile in semesterdata: 
    semester =  semesterfile[:-4].lower()
    constriant_file_name = "./constraints/bmcconstraints-" + semester + ".txt"
    studentpref_file_name = "./studentpreference/bmcstudentpref-" + semester + ".txt"
    output_file_name = "./outputschedule/output-" + semester + ".txt"
    prettyschedule_name = "./prettyschedule/prettyschedule-" + semester + ".txt"
    cmd = "python3 get_bmc_info.py data/{} {} {}".format(semesterfile, studentpref_file_name, constriant_file_name)
    subprocess.call(cmd)
    for iter in iterations:
        cmd = "python3 scheduling.py {} {} {} {}".format(constriant_file_name, studentpref_file_name, output_file_name, iter)
        prettyschedule = subprocess.check_output(cmd, shell= True)
        with open(prettyschedule_name, "ab") as file:
            file.write(prettyschedule)
