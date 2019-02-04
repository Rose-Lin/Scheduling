class estimation:
    def __init__(self, s, Pref, Schedule, Position, classes, rooms):
        self.s = s
        self.pref = Pref
        self.schedule = Schedule
        self.position = Position
        self.classes = classes
        self.rooms = rooms

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
        return (float(count)/total)

    def get_eval(self):
        return self.test_result(self.s, self.pref, self.schedule, self.position, self.classes, self.rooms)