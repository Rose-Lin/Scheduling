import sys
import time
import operator
import random
import math
from parse import *
from test_result import estimation

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

def init_overlapping_schedule(overlapping_slots, rooms):
    """A function that initialize a scheduling table for overlapping time slots"""
    num_rows = 0
    for days in overlapping_slots.keys():
        for group in overlapping_slots[days]:
            num_rows += len(group)-1
    overlapping_schedule= [[0 for y in rooms] for x in range(num_rows)]
    return overlapping_schedule

def fill_schedule(schedule, room_dict, Position,classes, i, students, professors,times, room_index_dict, hc_classes, ava_rooms, class_department, department_build):
    while i < len(classes):
        class_id = classes[i][0]
        if not class_id in hc_classes:
            i += 1
            continue
        major = class_department[class_id]
        possible_rooms = department_build[major]
        possible_room_index = {}
        for index, room in room_index_dict.items():
            if room[0] in possible_rooms:
                possible_room_index[index] = room
        popularity = classes[i][1]
        # index, t, cap = find_valid_reverse_room(schedule, popularity, possible_room_index, professors, class_id)
        index, t, cap = find_valid_room(schedule, popularity, possible_room_index, professors, class_id)
        if t == None:
            # Corner cases: when a specific room has very small capacity, so that the current class c cannot fit in any time of this room, and other rooms are all filled also.
            for ava_r in range(len(ava_rooms)):
                if ava_rooms[ava_r] > 0:
                    index = ava_r
            for row in range (len(schedule)):
                if schedule[row][index] == 0:
                    t = row
                    break
        if not t== None:
            ava_rooms[index] -= 1
            schedule[t][index] = class_id
            room_id = room_index_dict[index][0]
            room_dict[class_id] = (t+1,room_id)
            Position[class_id] = (t,index)
            i += 1
        else:
            return schedule, i
    return schedule, i

# classes is a list of clsses from count_class_size(), so it should be sorted by popularity already
# rooms should also be sorted list in increasing order of capacity (room_id, cap)
# overlapping_slots is a dictrionary of overlapping time slots. e.g. {'T,H': [[(1:00PM, 4:00PM), (2:30PM, 4:00PM),(12:00PM, 1:30PM)]]}
# times is a dictrionary of non-overlapping time slots
def scheduling(classes, students, professors, times, rooms, hc_classes, overlapping_slots, class_department, department_build):
    # schedule for non-overlapping time slots
    Schedule = [[0 for y in rooms] for x in times]
    overlapping_schedule = init_overlapping_schedule(overlapping_slots, rooms) # TODO: variable name
    room_index_dict = {}
    index = 0
    for room in rooms:
        room_index_dict[index] = room
        index += 1
    # Position is a dict keyed with class id
    Position = {}
    # room_dict is a dictrionary keyed with class id and (time slot,room id) in the schedule as value
    room_dict = {}
    # available rooms in the Schedule, the content of which is the number of slots that is available for the room
    ava_rooms = [len(times)]*len(rooms)
    i = 0
    Schedule, i = fill_schedule(Schedule,room_dict, Position, classes, i, students, professors, times, room_index_dict, hc_classes, ava_rooms, class_department, department_build)
    over_Position = {}
    if i < len(classes):
        # there are classes still not scheduled
        # move on to overlapping_schedule
        ava_rooms = [len(overlapping_schedule)]*len(rooms)
        overlapping_schedule, i = fill_schedule(overlapping_schedule,room_dict, over_Position, classes, i, students, professors, times, room_index_dict, hc_classes, ava_rooms, class_department, department_build)
        pass
    # print("----------non_overlapping Schedule-----------")
    # print (Schedule)
    # print("------------overlapping schedule-----------")
    # print(overlapping_schedule)
    # print("-----------Position-----------")
    # print(Position)
    # print('-----------Room dict--------')
    # print(room_dict)
    return Schedule+overlapping_schedule, Position, room_dict, over_Position

def simulatedAnnealing(initialSchedule, initialPosition, iterationMax, initial_temp, evaluation):
    room_index_dict = {}
    index = 0
    for room in evaluation.rooms:
        room_index_dict[index] = room
        index += 1
    temp_change_rate = 0.3
    curSchedule = initialSchedule
    bestSchedule = curSchedule
    curbestSatis = satisCalc(evaluation)
    curSatis = curbestSatis
    cur_temp = initial_temp # set as temp value, needs more research. TODO.
    for i in range (iterationMax):
        # neighborSchedule, neighborPosition = createNeighborSchedule_greedy(evaluation, room_index_dict, i)
        neighborSchedule, neighborPosition = createNeighborSchedule(evaluation, room_index_dict)
        evaluation.setSchedule(neighborSchedule, neighborPosition)
        neighborSatis = satisCalc(evaluation)
        #TODO change of temp 
        if curSatis < neighborSatis:
            curSchedule = neighborSchedule
            curSatis = neighborSatis
            if neighborSatis > curbestSatis:
                bestSchedule = neighborSchedule
                curbestSatis = neighborSatis
        elif(math.exp(float(curSatis - neighborSatis)/cur_temp) > 100):
            # TODO random() function
            curSchedule = neighborSchedule
    return bestSchedule, curbestSatis

def createNeighborSchedule(evaluation, room_index_dict):
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
    room_index, t, capacity = find_valid_room(NeighborSchedule, ran_class_cap, room_index_dict, evaluation.professors, ran_class_id)
    if not t== None:
        NeighborSchedule[old_time][old_room] = 0
        NeighborSchedule[t][room_index] = ran_class_id
        NeighborPosition[ran_class_id] = (t,room_index)
    return NeighborSchedule, NeighborPosition

def createNeighborSchedule_greedy(evaluation, room_index_dict, i):
    """ A function that creates a neighboring solution to the problem, by moving the most popular course to a valid empty time slot.
        Data such as schedule, position, students, pref, rooms, classes can be found in evaluation.
    """
    # create a new copy of schedule and position so that the original copies will not be changed in any ways.
    NeighborSchedule = evaluation.schedule.copy()
    NeighborPosition = evaluation.position.copy()
    # choose the most popular class indexed by i
    target_class = evaluation.classes[i]
    target_class_id = target_class[0]
    target_class_cap = target_class[1]
    old_time = evaluation.position[target_class_id][0]
    old_room = evaluation.position[target_class_id][1]
    room_index, t, capacity = find_valid_room(NeighborSchedule, target_class_cap, room_index_dict, evaluation.professors, target_class_id)
    if not t== None:
        NeighborSchedule[old_time][old_room] = 0
        NeighborSchedule[t][room_index] = target_class_id
        NeighborPosition[target_class_id] = (t,room_index)
    return NeighborSchedule, NeighborPosition


def satisCalc(evaluation):
    """A function that returns the satisfaction rate of the curent schedule associated with evaluation."""
    return evaluation.get_eval()

def find_valid_reverse_room(Schedule, threshold, room_index_dict, professors, class_id):
    room_id = 0
    t = None
    capacity = 0
    # total_rooms = len(rooms)
    index = 0
    for index, room in room_index_dict.items():
        room_id = room[0]
        capacity = room[1]
        t = empty_timeslot_reverse(Schedule, room_id, professors, class_id, index)
        if not t == None:
            break
    return index, t, capacity

def empty_timeslot_reverse(Schedule, room_id, professors, class_id, index):
    for row in range (len( Schedule)):
        professor_conflict = False
        if Schedule[row][index] == 0:
            for i in range (0, index):
                c_id = Schedule[row][i]
                if c_id > 0:
                    if professors[c_id] == professors[class_id]:
                        professor_conflict = True
                        break
            if professor_conflict == False:
                return row
    return None

def find_valid_room(Schedule, threshold, room_index_dict, professors, class_id):
    room_id = 0
    t = None
    capacity = 0
    # total_rooms = len(rooms)
    index = 0
    for index, room in room_index_dict.items():
        rid = room[0]
        cap = room[1]
        if cap >= threshold:
            room_id = rid
            capacity = cap
            t = empty_timeslot(Schedule, room_id, professors, class_id, index)
            if not t == None:
                break
    return index, t, capacity

def empty_timeslot(Schedule, room_id, professors, class_id, index):
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

def sort_room_cap(Class_list):
    Class_list.sort(key = lambda x: x[1])
    Class_list.reverse()
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

if len(sys.argv) != 4:
    print("Usage: " + 'python3' + " <constraints.txt> <student_prefs.txt> <schedule.txt>")
    exit(1)
start = time.time()

parser = parser()
professors, rooms, times, hc_classes, class_major, depart_build = parser.haverford_parse_prof_rooms_times_class(sys.argv[1])
time_group, time_no_dup = get_dup_time_slot_dict(times)
# time_no_dup is non-overlapping time slots
# time_group is overlapping time slots
times = haverford_reconstruct_time_slots(times)
time_no_dup = haverford_reconstruct_time_slots(time_no_dup)

pref_dict = parser.haverford_parse_pref(sys.argv[2])
students = pref_dict.keys()
classes = parser.count_class_size(pref_dict)
rooms = sort_room_cap(rooms)
schedule, position, room_dict, over_Position = scheduling(classes, students, professors, time_no_dup, rooms, hc_classes, time_group,class_major,depart_build)
end = time.time()
student_in_class = get_students_in_class(pref_dict, room_dict)
write_schedule_to_file(student_in_class, professors, room_dict, schedule, sys.argv[3])

sanitized = parser.sanitize_classes(hc_classes, classes)
eval = estimation(students, pref_dict, schedule, position, sanitized, rooms, professors)
print("satisfaction of greedy: {}".format(eval.get_eval()))
print("runtime: {}".format(end-start))

# start of simulated annealing
# iterationMax = 100
# initial_temp = 100
# bestsche, best_result = simulatedAnnealing(eval.schedule, eval.position, iterationMax, initial_temp, eval)
# print(best_result)
