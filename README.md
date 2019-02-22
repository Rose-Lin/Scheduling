# Scheduling

### Project Description

The goal of the project is to use a hybrid algorithm to solve the University Scheduling Problem. 

Some hard constraints have to be satisfied:
1. No professor can teach two cources at the same time.
2. No students can attend two cources at the same time.
3. Each department has a limited number of rooms that can be assigned to courses under that department.

Some soft constraints should be satisfied as much as possible:
1. Each student has a preference list that should be satisfied as much as possible.
2. Each room has a capacity and the students not able to fit in the room will be sacrificed.

The project implements a greedy algorithm to assign a basic schedule as an initial input for simulated annealing. Simulated annealing can generate a schedule that satisfies around 88% of the students' preferences.

### Requirements
* Make sure you have python 3.0 or later version installed.
* Also make sure you have tabulate module installed. If not, run command `pip install tabulate`

### How to execute the project
Go to directory `./data/haverford/`

If you do not have files named "haverfordConstrainsts_major.txt", run  `python3 .\get_haverford_info.py .\haverfordEnrollmentDataS14.csv .\haverfordStudentPrefs.txt .\haverfordConstraints_major.txt`
 
Then type in command `python3 .\scheduling.py .\haverfordConstraints_major.txt .\haverfordStudentPrefs.txt .\output.txt`. (`output.txt` is the file that stores the schedule generated with more detailed information on students attending each class. A more consice schedule is also printed in the shell, with a satifaction on the last line.)
