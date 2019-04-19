import csv
import sys
import os

def get_data_list_of_dicts():
    filename = "haverfordEnrollmentDataS14.csv"
    list = []
    with open(filename) as f:
        f_csv = csv.DictReader(f)
        for row in f_csv:
            list.append(row)
    return list

def get_courses(list_of_dicts):
    courses_name = {}
    department_pop = {}
    # ---------------BMC-------------
    # for dict in list_of_dicts:
    #     course = dict["Course ID"]
    #     prof = dict["Instructor ID"]
    #     campus = dict["Catalog"][0]
    #     room = dict["Facil ID 1"]
    #     subject = dict['Subject']
    #     if not course in courses_name and campus == "B" and room !="" and prof != '#Value!':
    #         courses_name[int(course)] = subject
    #         if subject in department_pop:
    #             department_pop[subject] += 1
    #         else:
    #             department_pop[subject] = 1
    # -----------------HC----------------
    for dict in list_of_dicts:
        course = dict["Course ID"]
        campus = dict["College"]
        room = dict["Facil ID 1"]
        subject = dict['Subject']
        if not course in courses_name and campus == "H" and room !="":
            courses_name[int(course)] = subject
            if subject in department_pop:
                department_pop[subject] += 1
            else:
                department_pop[subject] = 1
    # print(department_pop)
    # print(courses_name)
    return courses_name, department_pop

def courseid_name():
    list_of_dicts = get_data_list_of_dicts()
    course_name, department_pop = get_courses(list_of_dicts)
    return course_name, department_pop

# courseid_name()