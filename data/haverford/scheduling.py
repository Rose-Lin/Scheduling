import sys
import time
import operator
import random
from copy import deepcopy
from reextract_info import *
from decimal import *
from math import e
from parse import *
from test_result import estimation
from greedy import *

def get_dup_time_slot_dict(time_slots):
    # take in a dictrionary of time slots and output a dictionary where key is weekdays and value is the list of list of
    # overlapping time slots.
    time_slot_grouping = {}
    time_slot_no_overlapping = {}
    for days in time_slots.keys():
        # sort time slots by starting time:
        sort_by_start = sorted(time_slots[days], key = lambda x: x[0])
        same_time_list = []
        diff_time_list = []
        # sublist is the small group in that day
        sublist = []
        for index in range(len(sort_by_start)):
            elem = sort_by_start[index]
            if index == 0:
                diff_time_list.append(elem)
                sublist = [elem]
                latest_end_time = elem[1]

            # if the end time of the previous is later than the start time of this class
            elif latest_end_time > elem[0]:
                sublist.append(elem)
                if latest_end_time < elem[1]:
                    latest_end_time = elem[1]

            # if there is no overlapping, start a new list
            else:
                if len(sublist) > 1:
                    same_time_list.append(sublist)
                sublist = [elem]
                diff_time_list.append(elem)
                latest_end_time = elem[1]

        # if more than 1 class in cluster, add the cluster into the same group, if just 1 class, no conflict, don't add
        if len(sublist) > 1:
            same_time_list.append(sublist)
        time_slot_grouping[days] = same_time_list
        time_slot_no_overlapping[days] = diff_time_list
    return time_slot_grouping, time_slot_no_overlapping

def haverford_reconstruct_time_slots(time_slots):
    """ A function reconstruct a dictrionary of time_slots to a list, so that it is ready to be passed into scheduling function"""
    times = []
    for day, periods in time_slots.items():
        for slot in periods:
            times.append((day, slot))
    return times


def simulatedAnnealing(initialSchedule, initialPosition, iterationMax, evaluation, conflict_pair, maximum, course_name, NS_id):
    getcontext().prec = 6
    getcontext().traps[Overflow] = 0
    bestSchedule = deepcopy(initialSchedule)
    bestPosition = deepcopy(initialPosition)
    result = satisCalc(evaluation, course_name, False)
    curbestSatis = result[0]
    total = result[1]
    for i in range (iterationMax):
        if NS_id == "NS1":
            neighborSchedule, neighborPosition = createNeighborSchedule(evaluation)
        elif NS_id == "NS2":
            neighborSchedule, neighborPosition = createNeighborSchedule_NS2(evaluation)
        elif NS_id == "NS3":
            neighborSchedule, neighborPosition = createNeighborSchedule_greedy(evaluation, i%len(evaluation.classes))
        else:
            neighborSchedule, neighborPosition = createNeighborSchedule_conflict_pair(evaluation, conflict_pair, maximum,  i%len(evaluation.classes))
        evaluation.setSchedule(neighborSchedule, neighborPosition)
        neighborSatis = satisCalc(evaluation, course_name, False)[0]
        if curbestSatis < neighborSatis:
            bestSchedule = deepcopy(neighborSchedule)
            bestPosition = deepcopy(neighborPosition)
            neighborSchedule[0][-1] = 0
            curbestSatis = neighborSatis
        else:
            evaluation.setSchedule(bestSchedule, bestPosition)
    return bestSchedule, curbestSatis, total

def createNeighborSchedule_conflict_pair(evaluation, conflict_pair, maximum, i):
    """ This neighborhood structure finds the most conflicted class with class i and reassigns i to other timeslot"""
    NeighborSchedule = evaluation.schedule.copy() 
    NeighborPosition = evaluation.position.copy()
    # Assuming the most popular class will have the most conflict, so conflict_pair does not need to be sorted
    target_class1 = evaluation.classes[i]
    target_class1_id = target_class1[0]
    target_class1_cap = target_class1[1]
    if not target_class1_id in conflict_pair:
        return NeighborSchedule, NeighborPosition
    target_class2_dic = conflict_pair[target_class1_id]
    largest_conflict_num = 0
    target_class2_id = target_class1
    target_class2_cap = -1
    # Find target_class2_id, which is the most conflict class with class1
    for class2, conflict_num in target_class2_dic.items():
        if largest_conflict_num < conflict_num:
            target_class2_id = class2
            largest_conflict_num = conflict_num
    for c, pop in evaluation.classes:
        if c == target_class2_id:
            target_class2_cap = pop
    # Raise error when no target2 is found in evaluation.classes. Hope this will no happen
    if target_class2_cap == -1:
        print("conflicted class not found, error!!")
        return NeighborSchedule, NeighborPosition
    old_time1 = evaluation.position[target_class1_id][0]
    old_room1 = evaluation.position[target_class1_id][1]
    old_time2 = evaluation.position[target_class2_id][0]
    old_room2 = evaluation.position[target_class2_id][1]
    # Reassign class1 
    # Logistic behind: every class is gauranteed to be reassigned at least once, with its most conflicted class
    room_index, t, capacity = find_valid_room_SA(NeighborSchedule, target_class1_cap, evaluation.room_index_dict, evaluation.professors, target_class1_id)    
    if (not t== None) and (not t == old_time2):
        NeighborSchedule[old_time1][old_room1] = 0
        NeighborSchedule[t][room_index] = target_class1_id
        NeighborPosition[target_class1_id] = (t,room_index)
    return NeighborSchedule, NeighborPosition

def createNeighborSchedule_NS2(evaluation):
    # create a new copy of schedule and position so that the original copies will not be changed in any ways.
    NeighborSchedule = evaluation.schedule.copy() 
    NeighborPosition = evaluation.position.copy()
    # randomly choose two classes
    ran_class_pair1 = random.choice(evaluation.classes)
    ran_class_pair2 = random.choice(evaluation.classes)
    ran_class_id1 = ran_class_pair1[0]
    ran_class_id2 = ran_class_pair2[0]
    old_time1 = evaluation.position[ran_class_id1][0]
    old_room1 = evaluation.position[ran_class_id1][1]
    old_time2 = evaluation.position[ran_class_id2][0]
    old_room2 = evaluation.position[ran_class_id2][1]
    NeighborSchedule[old_time1][old_room1] = ran_class_id2
    NeighborSchedule[old_time2][old_room2] = ran_class_id1
    NeighborPosition[ran_class_id1] = (old_time2,old_room2)
    NeighborPosition[ran_class_id2] = (old_time1,old_room1)
    return NeighborSchedule, NeighborPosition

def createNeighborSchedule(evaluation):
    """ A function that creates a neighboring solution to the problem, by moving a random course to a random empty time slot.
        Data such as schedule, position, students, pref, rooms, classes can be found in evaluation.
    """
    # create a new copy of schedule and position so that the original copies will not be changed in any ways.
    NeighborSchedule = evaluation.schedule.copy() 
    NeighborPosition = evaluation.position.copy()
    # randomly choose a class
    ran_class_pair = random.choice(evaluation.classes)
    ran_class_id = ran_class_pair[0]
    ran_class_cap = ran_class_pair[1]
    old_time = evaluation.position[ran_class_id][0]
    old_room = evaluation.position[ran_class_id][1]
    room_index, t, capacity = find_valid_room(NeighborSchedule, ran_class_cap, evaluation.room_index_dict, evaluation.professors, ran_class_id)
    if not t== None:
        NeighborSchedule[old_time][old_room] = 0
        NeighborSchedule[t][room_index] = ran_class_id
        NeighborPosition[ran_class_id] = (t,room_index)
    return NeighborSchedule, NeighborPosition

def createNeighborSchedule_greedy(evaluation, i):
    """ A function that creates a neighboring solution to the problem, by moving the most popular course to a valid empty time slot.
        Data such as schedule, position, students, pref, rooms, classes can be found in evaluation.
    """
    # create a new copy of schedule and position so that the original copies will not be changed in any ways.
    NeighborSchedule = evaluation.schedule.copy()
    NeighborPosition = evaluation.position.copy()
    # choose the most popular class indexed by i
    # If moving the least popular class, change i to -i
    target_class = evaluation.classes[i]
    target_class_id = target_class[0]
    target_class_cap = target_class[1]
    old_time = evaluation.position[target_class_id][0]
    old_room = evaluation.position[target_class_id][1]
    room_index, t, capacity = find_valid_room_SA(NeighborSchedule, target_class_cap, evaluation.room_index_dict, evaluation.professors, target_class_id)
    if not t== None:
        NeighborSchedule[old_time][old_room] = 0
        NeighborSchedule[t][room_index] = target_class_id
        NeighborPosition[target_class_id] = (t,room_index)
    return NeighborSchedule, NeighborPosition

def find_valid_room_SA(Schedule, threshold, room_index_dict, professors, class_id):
    """A function that finds a valid room (without professor conflict) that is large enough to hold the class, without sacrificing any students."""
    room_id = 0
    t = None
    capacity = 0
    index = 0
    for index, room in room_index_dict.items():
        rid = room[0]
        cap = room[1]
        if cap >= threshold:
            room_id = rid
            capacity = cap
            index = random.randint(index, len(room_index_dict)-1) #88.4% with 5000 iteration (NS3)
            t = empty_timeslot_SA(Schedule, room_id, professors, class_id, index, room_index_dict)
            if not t == None:
                break
    return index, t, capacity

def empty_timeslot_SA(Schedule, room_id, professors, class_id, index, room_index_dict):
    """Different from greedy: Find any room that is large enough, instead of finding one that is as small as possible to hold the popularity"""
    for row in range (len( Schedule)):
        professor_conflict = False
        if Schedule[row][index] == 0:
            for i in range (len(Schedule[0])):
                c_id = Schedule[row][i]
                if c_id > 0:
                    if professors[c_id] == professors[class_id]:
                        professor_conflict = True
                        break
            if professor_conflict == False:
                return row
    return None

def satisCalc(evaluation, course_name, display_failure = False):
    """A function that returns the satisfaction rate of the curent schedule associated with evaluation."""
    return evaluation.get_eval(course_name, display_failure)

def sort_room_cap(Class_list):
    Class_list.sort(key = lambda x: x[1])
    # Class_list.reverse()
    # Important!!!!!
    # Wether to reverse the list depends on how many rooms there are and the room capacity
    return Class_list

def write_schedule_to_file(s_in_c, prof, room_dict, schedule, file):
    f = open(file, 'w')
    f.write("Course\tRoom\tTeacher\tTime\tStudents\n")
    for c in s_in_c:
        if c in room_dict.keys():
            f.write(str(c)+ "\t")
            f.write(str(room_dict[c][1]) + "\t")
            f.write(str(prof[c]) + "\t")
            f.write(str(room_dict[c][0]) + "\t")
            f.write(''.join(str(e) + " " for e in s_in_c[c]))
            f.write("\n")
    f.close()

def get_students_in_class(pref_dict, room_dict):
    students = {}
    for s in pref_dict:
        times = []
        for c in pref_dict[s]:
            if c in room_dict.keys():
                if room_dict[c][0] not in times:
                    times.append(room_dict[c][0])
                    if c in students:
                        students[c].append(s)
                    else:
                        students[c] = [s]
    return students

if len(sys.argv) != 6:
    print("Usage: " + 'python3 scheduling.py' + " <constraints.txt> <student_prefs.txt> <schedule_output.txt> <#iteration> <neighboring stucture id>")
    exit(1)
start = time.time()
parser = parser()
professors, rooms, times, hc_classes, class_major, depart_build = parser.haverford_parse_prof_rooms_times_class(sys.argv[1])
time_group, time_no_dup = get_dup_time_slot_dict(times) # time_no_dup is non-overlapping time slots
                                                        # time_group is overlapping time slots
times = haverford_reconstruct_time_slots(times)
time_no_dup = haverford_reconstruct_time_slots(time_no_dup)
pref_dict = parser.haverford_parse_pref(sys.argv[2], hc_classes)
students = pref_dict.keys()
classes = parser.count_class_size(pref_dict) #classes is sorted by pop
rooms = sort_room_cap(rooms)
room_index_dict = {}
index = 0

# course_name, department_pop = courseid_name()
course_name = {}
# find the conflict pair
if sys.argv[5] == "NS4":
    conflict_pair, maximum = parser.conflict_pair(hc_classes, pref_dict)
else:
    conflict_pair = {}
    maximum = 0

for room in rooms:
    room_index_dict[index] = room
    index += 1
schedule, position, room_dict, over_Position = scheduling(classes, students, professors, time_no_dup, rooms, hc_classes, time_group,class_major,depart_build, room_index_dict)
student_in_class = get_students_in_class(pref_dict, room_dict)

sanitized = parser.sanitize_classes(hc_classes, classes)
eval = estimation(students, pref_dict, schedule, position, sanitized, rooms, professors, room_index_dict)
greedy_result = satisCalc(eval,course_name)
print("Satisfaction of greedy: {}".format(greedy_result[0]/greedy_result[1]))
# print("runtime: {}".format(end-start))

# start of simulated annealing
iterationMax = int(sys.argv[4] )
NS_id = sys.argv[5]
bestsche, best_result, total = simulatedAnnealing(schedule, position, iterationMax, eval, conflict_pair, maximum, course_name, NS_id)
end = time.time()
print("Satisfaction of Simulated Annealing:\n iteration: {} \t runtime: {} \t SAT: {}".format(sys.argv[4],end-start, Decimal(best_result/total)*100 ))

# eval does not have the best schedule. #TODO
eval.displaySchedule(time_no_dup) 
result = satisCalc(eval, course_name, False)
# print("This schedule is satisfying {}% of student preference".format(Decimal(best_result/total)*100) )
write_schedule_to_file(student_in_class, professors, room_dict, schedule, sys.argv[3])