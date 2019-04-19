import operator

class parser:
    def haverford_parse_prof_rooms_times_class(self, file):
        """" A function used on haverford data, returns professors list, rooms list and time slots list"""
        with open(file) as f:
            raw_content =  f.read().strip()
            lines = raw_content.split('\n')
            total_time_slots = int(lines[0].split('\t')[1])
            time_slots = {}
            for i in range(1, total_time_slots+1):
                times = lines[i].split('\t')[1].split()
                start_time = times[0]+times[1]
                end_time = times[2]+times[3]
                days = times[4:]
                # time_slots is a dictrionary with group of days (e.g.'T,H' or 'F') as key and the [(start_time, end_time)] as value
                time_slots = self.get_time_slot_dict(start_time, end_time, days, time_slots)
            # room_line_num is the line of which the information about rooms starts
            room_line_num = 1+total_time_slots
            total_rooms = int(lines[room_line_num].split('\t')[1])
            # rooms is a list of tuples [(room_name, cap)]
            rooms = []
            for i in range(1+room_line_num, 1+room_line_num+total_rooms):
                room_name = lines[i].split('\t')[0]
                cap = int(lines[i].split('\t')[1])
                rooms.append((room_name, cap))
            # class_line_num is the line of which the information about classes and teachers starts
            class_line_num = 1+room_line_num+total_rooms
            total_classes = int(lines[class_line_num].split('\t')[1])
            total_teachers = int(lines[class_line_num+1].split('\t')[1])
            # profs is a dictrionary, with keys as class id and professors id as value
            profs = {}
            # haverford classes excluding labs and bmc classes
            hc_classes = []
            # class_major is {class_id: major}
            class_major = {}
            depart_build = {}
            for i in range(class_line_num+2, class_line_num+total_classes+2):
                tokenizes = lines[i].split('\t')
                class_id = int(tokenizes[0])
                # TODO: this is not considering the labs
                if tokenizes[1]:
                    prof_id = int(tokenizes[1])
                    major = tokenizes[2]
                    possible_rooms = tokenizes[3:]
                    profs[class_id] = prof_id
                    class_major[class_id] = major
                    depart_build[major] = possible_rooms
                    hc_classes.append(class_id)
        return profs, rooms, time_slots, hc_classes, class_major, depart_build

    def get_time_slot_dict(self, start_time, end_time, days, time_slots):
        time_slots_keys = ''
        for day in days:
            time_slots_keys += day + ','
        time_slots_keys = time_slots_keys[:-1]
        if time_slots_keys in time_slots.keys():
            time_slots[time_slots_keys].append((start_time, end_time))
        else:
            time_slots[time_slots_keys] = [(start_time, end_time)]
        return time_slots

    def haverford_parse_pref(self, file, hc_classes):
        """" A function used on haverford data, returns professors students pref dict"""
        pref_dict = {}
        with open(file) as f:
            raw_content = f.read().strip()
            lines = raw_content.split('\n')
            total_student_num = int(lines[0].split('\t')[1])
            for i in range(1, 1+total_student_num):
                student_id = int(lines[i].split('\t')[0])
                pref_list_line = lines[i].split('\t')[1]
                pref_dict[student_id] = [int(x) for x in pref_list_line.split()]
        pref_dict = self.sanitize_pref(pref_dict, hc_classes)
        return pref_dict
    
    def sanitize_pref(self, pref_dict, hc_classes):
        """A function that eliminates all Bryn Mawr classes from students' preference dicts, and removes duplicate classes from the pref list."""
        for student_id, pref_list in pref_dict.items():
            sanitized_pref = []
            d ={}
            for class_id in pref_list:
                d[class_id] = False
            for class_id in pref_list:
                d[class_id] = not d[class_id]
                if class_id in hc_classes:
                    if d[class_id]:
                        sanitized_pref.append(class_id)
            pref_dict[student_id] = sanitized_pref
        return pref_dict

    def count_class_size(self, pref_dict):
        sizes = {}
        for x in pref_dict:
            for index in set(pref_dict[x]):
                if index in sizes.keys():
                    sizes[index] += 1
                else:
                    sizes[index] = 1
        # n is the sorted classes list according to popularity
        # content in n: (class id, popularity)
        n = sorted(sizes.items(), key=operator.itemgetter(1))
        n.reverse()
        return n
    
    def sanitize_classes(self, hc_classes, classes):
        """classes: [(class_id, popularity)]
            hc_classes: [classes_id]
        """
        sanitized = []
        for pair in classes:
            if pair[0] in hc_classes:
                sanitized.append(pair)
        return sanitized
    
    def conflict_pair(self, hc_classes, pref_dict):
        """conflict_pair = {class1: {class2: conflict_num}, class2: {class1: conflict_num}}"""
        conflict_pair = {}
        maximum = 0
        for student, pref_list in pref_dict.items():
            if len(pref_dict) <= 1:
                pass
            for i in range (len(pref_list)-1):
                if not pref_list[i] in conflict_pair:
                    conflict_pair[pref_list[i]] = {}
                for j in range (i+1, len(pref_list)):
                    if not pref_list[j] in conflict_pair:
                        conflict_pair[pref_list[j]] = {}
                    if pref_list[j] in conflict_pair[pref_list[i]]:
                        conflict_pair[pref_list[i]][pref_list[j]] += 1
                    else:
                        conflict_pair[pref_list[i]][pref_list[j]] = 1
                    if pref_list[i] in conflict_pair[pref_list[j]]:
                        conflict_pair[pref_list[j]][pref_list[i]] += 1
                    else:
                        conflict_pair[pref_list[j]][pref_list[i]] = 1
                    if maximum < conflict_pair[pref_list[i]][pref_list[j]]:
                        maximum = conflict_pair[pref_list[i]][pref_list[j]]
        return conflict_pair, maximum
    
    def sort_conflict_pair(self,conflict_pair, maximum):
        """sorted_conflict_pair = {conflict_num : (class1, class2)}
        (class1, class2) and (class2, class1) <-- only one of them appears in the dictionary
        """
        sorted_conflict_pair = {}
        for  class1, dic in conflict_pair.items():
            for class2, conflict_num in dic.items():
                if conflict_num in sorted_conflict_pair:
                    if( not (class1, class2) in sorted_conflict_pair[conflict_num] )and (not (class2, class1) in sorted_conflict_pair[conflict_num] ):
                        sorted_conflict_pair[conflict_num].append((class1, class2))
                else:    
                    sorted_conflict_pair[conflict_num] = [(class1, class2)]
        return sorted_conflict_pair