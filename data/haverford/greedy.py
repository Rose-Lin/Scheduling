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
        # `find_valid_reverse_room` is not used because it will lower the optimality.
        # Reason: used up all time slots for largest rooms will cause some class to be assigned to rooms not large enough
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
def scheduling(classes, students, professors, times, rooms, hc_classes, overlapping_slots, class_department, department_build, room_index_dict):
    # schedule for non-overlapping time slots
    Schedule = [[0 for y in rooms] for x in times]
    overlapping_schedule = init_overlapping_schedule(overlapping_slots, rooms) # TODO: variable name
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
    # return Schedule+overlapping_schedule, Position, room_dict, over_Position
    return Schedule, Position, room_dict, over_Position

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

def init_overlapping_schedule(overlapping_slots, rooms):
    """A function that initialize a scheduling table for overlapping time slots"""
    num_rows = 0
    for days in overlapping_slots.keys():
        for group in overlapping_slots[days]:
            num_rows += len(group)-1
    overlapping_schedule= [[0 for y in rooms] for x in range(num_rows)]
    return overlapping_schedule