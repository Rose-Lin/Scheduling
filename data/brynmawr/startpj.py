# -*- coding: utf-8 -*-
import os
import sys
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
    print("dir \'prettyschedule\' already exists")

if len(sys.argv) == 2 and sys.argv[-1] == "-h":
    print("Choices of <neighboring stucture>: NS1\t NS2\t NS3 \t NS4")
    print("# of iteration of simualted annealing: \n- For every 1000 iteration of simulated annealing, the program runs roughly 10 seconds.")
    print("- Suggested number of iterations: 2500")
    print("Semester:\n-To run on all semesters, use all.")
    print("-Pick one semester from Fall2000 to Spring2015. All names of avalilable semester can be found under directory \"./data/\".")
    exit(1)
elif len(sys.argv) != 4:
	print("Usage: " + 'python3 startpj.py' + "<# of iteration of simulated annealing> <neighboring structure> <semester>")
	print("Please type python3 startpj.py -h for help.")
	exit(1)

iterations = [sys.argv[1]]
NS_id = sys.argv[2]
semester_check = sys.argv[3]
if NS_id != "NS1" and NS_id != "NS2" and NS_id != "NS3" and NS_id !="NS4":
	print("Please give the correct neighboring structure. \n-h for more information.")
	exit(1)

if semester_check != "all":
    semester = semester_check + ".csv"
    if not os.path.isfile("./data/"+semester):
        print("<semester> is not correct.")
        exit(1)
    semesterdata = [semester]

for semesterfile in semesterdata: 
    semester =  semesterfile[:-4].lower()
    constriant_file_name = "./constraints/bmcconstraints-" + semester + ".txt"
    studentpref_file_name = "./studentpreference/bmcstudentpref-" + semester + ".txt"
    output_file_name = "./outputschedule/output-" + semester + ".txt"
    prettyschedule_name = "./prettyschedule/prettyschedule-" + semester +".txt"
    cmd = "python3 get_bmc_info.py data/{} {} {}".format(semesterfile, studentpref_file_name, constriant_file_name)
    subprocess.call(cmd)
    for iter in iterations:
        for i in range (1):
            cmd = "python3 ../haverford/scheduling.py {} {} {} {} {}".format(constriant_file_name, studentpref_file_name, output_file_name, iter, NS_id)
            prettyschedule = subprocess.check_output(cmd, shell= True)
            with open(prettyschedule_name, "wb") as file:
                file.write(prettyschedule)
