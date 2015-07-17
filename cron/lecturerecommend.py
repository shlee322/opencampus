from opencampus.common.db import db
from opencampus.common.models import Campus
from opencampus.module.lecture.models import Lecture, LectureAnalogue


def load_student_ids(campus_id):
    page = 0

    student_ids = []

    while True:
        lectures = Lecture.objects(campus_id=campus_id).skip(20*page).limit(20)

        if len(lectures) < 1:
            break

        print('load page %s' % page)
        for lecture in lectures:
            for student in lecture.students:
                student_ids.append(student)

        page += 1

    student_ids = list(set(student_ids))
    student_ids.sort(reverse=True)

    return student_ids


def check_data(campus_id, student_id1, lectures1, student_id2, lectures2):
    if student_id1 == student_id2:
        return

    lectures1 = set([l.subject_code for l in lectures1])
    lectures2 = set([l.subject_code for l in lectures2])

    analogue = len(lectures1 & lectures2)/len(lectures1 | lectures2)
    if analogue >= 1.0:
        return

    try:
        analogue_obj = LectureAnalogue.objects(
            campus_id=campus_id,
            student_id=student_id1
        ).get()

        if analogue_obj.point >= analogue:
            return
    except:
        analogue_obj = LectureAnalogue(
            campus_id=campus_id,
            student_id=student_id1
        )

    analogue_obj.point = analogue
    analogue_obj.target = student_id2
    analogue_obj.save()

    print('%s-%s %s' % (student_id1, student_id2, analogue))


campus_page = 0

while True:
    campuses = Campus.objects().skip(20*campus_page).limit(20)

    if len(campuses) < 1:
        break

    campus_page += 1

    for campus in campuses:
        campus_student_ids = load_student_ids(campus.id)

        for student_id1 in campus_student_ids:
            lecture1 = Lecture.objects(students__in=[student_id1], campus_id=campus.id)
            for student_id2 in campus_student_ids:
                lecture2 = Lecture.objects(students__in=[student_id2], campus_id=campus.id)

                check_data(campus.id, student_id1, lecture1, student_id2, lecture2)
