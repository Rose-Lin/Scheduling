import tabulate
import decimal

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
        # print(room_index_dict)
        # print("professors:")
        # print(professors)
        # print("position")
        # print(Position)
        # print(classes)
        
    def setSchedule(self,newSchedule, newPosition):
        self.schedule = newSchedule
        self.position = newPosition

    def test_result(self, S, Pref, Schedule, Position, classes, rooms):
        """s : students"""
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
        # print(total) #-->3334
        # return (decimal.Decimal(count)/total)
        # return (float(count)/total)
        return count, total

    def get_eval(self):
        # TODO: need to update based on self.test_result
        return self.test_result(self.s, self.pref, self.schedule, self.position, self.classes, self.rooms)[0]

    def displaySchedule(self, time_no_dup):
        header = ["course_id", "professors", "time","room", "popularity"]
        table = []
        for row_num in range (len(self.schedule)):
            for col_num in range (len(self.schedule[0])):
                if self.schedule[row_num][col_num] != 0:
                    course_id = self.schedule[row_num][col_num]
                    time = time_no_dup[row_num]
                    room = self.room_index_dict[col_num]
                    prof = self.professors[course_id]
                    popularity = -1
                    for pair in self.classes:
                        if pair[0] == course_id:
                            popularity = pair[1]
                    row = [course_id, prof, time, room, popularity]
                    table.append(row)
        print(tabulate.tabulate(table, header,  tablefmt="github"))