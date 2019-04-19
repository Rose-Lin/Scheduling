import tabulate
import decimal
from copy import deepcopy

class estimation:
    def __init__(self, s, Pref, Schedule, Position, classes, rooms, professors, room_index_dict):
        self.s = s
        self.pref = Pref
        self.schedule = Schedule
        self.position = Position
        self.classes = classes
        self.rooms = rooms
        self.professors = professors
        self.room_index_dict = room_index_dict
        
    def setSchedule(self,newSchedule, newPosition):
        self.schedule = deepcopy(newSchedule)
        self.position = deepcopy(newPosition)

    def test_result(self, S, Pref, Schedule, Position, classes, rooms, course_name, display_failure= False):
        """s : students"""
        # failure_record = {}
        count = 0
        total = 0
        for s in S:
            total += len(Pref[s])
            final_pick = [0] * (len(Schedule)+1)
            for c in Pref[s]:
                if c in Position:
                    t_index = Position[c][0]
                    if final_pick[t_index] == 0:
                        final_pick[t_index] = c
                        count += 1
                    # else:
                    #     # s is already taking classes at time t_index
                    #     failure = (course_name[c], course_name[final_pick[t_index]])
                    #     failure_reverse = (course_name[final_pick[t_index]], course_name[c])
                    #     if failure in failure_record:
                    #         failure_record[failure] += 1
                    #     elif failure_reverse in failure_record:
                    #         failure_record[failure_reverse] += 1
                    #     else:
                    #         failure_record[failure] = 1
                else:
                    total -= 1
        for c in Position.keys():
            r_index = Position[c][1]
            room_cap = rooms[r_index][1]
            pop = 0
            for pair in classes:
                if c == pair[0]:
                        pop = pair[1]
            if pop > room_cap:
                count -= (pop-room_cap)
        # if display_failure:
        #     print(failure_record)
        return count, total

    def get_eval(self, course_name, display_failure):
        result = self.test_result(self.s, self.pref, self.schedule, self.position, self.classes, self.rooms, course_name, display_failure)
        return result

    def displaySchedule(self, time_no_dup):
        header = ["course_id", "professors", "time","room", "popularity"]
        table = []
        dic = {}
        for c in self.classes:
            dic[c[0]] = False
        for row_num in range (len(self.schedule)):
            for col_num in range (len(self.schedule[0])):
                if self.schedule[row_num][col_num] != 0:
                    course_id = self.schedule[row_num][col_num]
                    if not dic[course_id]:
                        dic[course_id] = True
                    else:
                        print("duplicates in schedule {}".format(course_id))
                    time = time_no_dup[row_num]
                    room = self.room_index_dict[col_num]
                    prof = self.professors[course_id]
                    popularity = -1
                    for pair in self.classes:
                        if pair[0] == course_id:
                            popularity = pair[1]
                    row = [course_id, prof, time, room, popularity]
                    table.append(row)
        for k, v in dic.items():
            if v == False:
                print(str(k) + " is not assigned a time slot")
        print(tabulate.tabulate(table, header,  tablefmt="github"))