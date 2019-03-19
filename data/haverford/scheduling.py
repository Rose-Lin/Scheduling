import sys
import time
import operator
import random
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


def simulatedAnnealing(initialSchedule, initialPosition, iterationMax, initial_temp, evaluation):
    # print (evaluation.room_index_dict)
    getcontext().prec = 6
    getcontext().traps[Overflow] = 0
    temp_change_rate = Decimal(0.002)
    curSchedule = initialSchedule
    bestSchedule = curSchedule
    curbestSatis = satisCalc(evaluation)
    curSatis = curbestSatis
    cur_temp = Decimal(initial_temp) # set as temp value, needs more expemeriments. TODO.
    T_min = Decimal(0.1)
    # while cur_temp > T_min:
    for i in range (iterationMax):
        # hybrid SA
        if cur_temp > T_min:
            # neighborSchedule, neighborPosition = createNeighborSchedule_greedy(evaluation, i%len(evaluation.classes))
            neighborSchedule, neighborPosition = createNeighborSchedule(evaluation)
            evaluation.setSchedule(neighborSchedule, neighborPosition)
            neighborSatis = satisCalc(evaluation)
            cur_temp = Decimal(cur_temp*(1-temp_change_rate)) #only apply this when use createNeighborSchedule_greedy
            if curSatis < neighborSatis:
                curSchedule = neighborSchedule
                curSatis = neighborSatis
                if neighborSatis > curbestSatis:
                    bestSchedule = neighborSchedule
                    curbestSatis = neighborSatis
                # print("accept, curbest : {} at iteration i={}".format(curbestSatis/3878, i))
                # print(bestSchedule)
            elif Decimal(e)**(Decimal((curSatis - neighborSatis)/Decimal(cur_temp))) < random.uniform(1.7,1.75) and Decimal(e)**(Decimal((curSatis - neighborSatis)/Decimal(cur_temp))) > random.uniform(1.65,1.7): 
                # print("!!! {} {} {}".format((curSatis - neighborSatis), (cur_temp), (Decimal(e)**(Decimal((curSatis - neighborSatis)/Decimal(cur_temp))))))
                curSchedule = neighborSchedule
                curbestSatis = neighborSatis
                # print("jump out curstatis: {}  neighborsatis:{}, curbest: {}".format(curSatis ,neighborSatis, curbestSatis))
            # cur_temp = Decimal(cur_temp*(1-temp_change_rate)) #only apply this when use createNeighborSchedule_greedy
            # print(curbestSatis, 
            # cur_temp, 
            # curSatis - neighborSatis, Decimal(e)**(Decimal((curSatis - neighborSatis)/Decimal(cur_temp))))
        # else:
        #     cur_temp = initial_temp
    return bestSchedule, curbestSatis/3334

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
    # room_index, t, capacity = find_valid_room(NeighborSchedule, target_class_cap, evaluation.room_index_dict, evaluation.professors, target_class_id)
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
            index = random.randint(index, len(room_index_dict)-1) #88.4% with 5000 iteration 
            # if index < len(room_index_dict)-1:
            #     index += 1    #around 82.4% wiht 5000 iteration
            # if index < len(room_index_dict)-20:
            #     index += 20    #around 86% wiht 5000 iteration
            # 85.67% without further manipulating index at all with 5000 iteration
            # 82% complete randomness with 5000 iteration
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

def satisCalc(evaluation):
    """A function that returns the satisfaction rate of the curent schedule associated with evaluation."""
    return evaluation.get_eval()

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

if len(sys.argv) != 5:
    print("Usage: " + 'python3' + " <constraints.txt> <student_prefs.txt> <schedule_output.txt> <#iteration>")
    exit(1)
start = time.time()
print("---------------------------------{} iteration-----------------".format(sys.argv[4]))
parser = parser()
professors, rooms, times, hc_classes, class_major, depart_build = parser.haverford_parse_prof_rooms_times_class(sys.argv[1])
time_group, time_no_dup = get_dup_time_slot_dict(times)
# time_no_dup is non-overlapping time slots
# time_group is overlapping time slots
times = haverford_reconstruct_time_slots(times)
time_no_dup = haverford_reconstruct_time_slots(time_no_dup)
pref_dict = parser.haverford_parse_pref(sys.argv[2], hc_classes)
students = pref_dict.keys()
classes = parser.count_class_size(pref_dict)
rooms = sort_room_cap(rooms)
room_index_dict = {}
index = 0
for room in rooms:
    room_index_dict[index] = room
    index += 1
schedule, position, room_dict, over_Position = scheduling(classes, students, professors, time_no_dup, rooms, hc_classes, time_group,class_major,depart_build, room_index_dict)
student_in_class = get_students_in_class(pref_dict, room_dict)
# write_schedule_to_file(student_in_class, professors, room_dict, schedule, sys.argv[3])

sanitized = parser.sanitize_classes(hc_classes, classes)
eval = estimation(students, pref_dict, schedule, position, sanitized, rooms, professors, room_index_dict)
print("satisfaction of greedy: {}".format(eval.get_eval()/3334))
# print("runtime: {}".format(end-start))

# start of simulated annealing
iterationMax = int(sys.argv[4] )
initial_temp = Decimal(100000)
bestsche, best_result = simulatedAnnealing(eval.schedule, eval.position, iterationMax, initial_temp, eval)
end = time.time()
print("runtime: {}".format(end-start))
# eval.displaySchedule(time_no_dup)
print("This schedule is satisfying {}% of student preference".format(Decimal(best_result)*100) )
write_schedule_to_file(student_in_class, professors, room_dict, schedule, sys.argv[3])