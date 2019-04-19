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

The project implements a two-phased algorithm: greedy combined with hybrid simulated annealing algorithm. This algorithm can generate schedules that satisfy around 95% of the students' preferences.

### Requirements
* Make sure you have python 3.0 or later version installed.
* Also make sure you have tabulate module installed. If not, run command `pip install tabulate`

### How to execute the project
#### Haverford Data
Go to directory `./data/haverford/`

To run the project, use `python3 startpj.py <number of iterations for simulated annealing> <neighboring structure>`. For more information on how to run the project, use `python3 startpj.py -h`.

The final human readable schedule, together with the optimality result, can be found under in the file named `preetyschedule.txt`. Another copy of the schedule is wirtten into `output.txt`, which is used to pass the validity test.

#### Bryn Mawr Data
Go to directory `./data/brynmawr/`

To run the project, use `python3 startpj.py <number of iteration of simulated annealing> <neighboring structure> <semester>`. For more information on how to run the project, use `python3 startpj.py -h`. If you want to test the algorithm on all 30 semesters, use `all` for `<semester>`.

The final human readable schedule, together with the optimality result, can be found under the directory `./preetyschedule`. Each semester will have its own schedule output. Another copy of the schedule is wirtten into `output.txt`, which is used to pass the validity test.

### How to test the validity of the schedule
Run `is_valid.pl` with the corresponding constraint and preference files.