# -*- coding: utf-8 -*-
# Copyright (C) 2015 opencampus.kr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mongoengine import Document, EmbeddedDocument, fields
from . import searchengine


class LectureTime(EmbeddedDocument):
    place = fields.StringField()
    room = fields.StringField()
    start_time = fields.IntField()
    end_time = fields.IntField()


class Professor(Document):
    campus_id = fields.ObjectIdField()
    name = fields.StringField()
    phone = fields.StringField()
    email = fields.EmailField()


class Lecture(Document):
    campus_id = fields.ObjectIdField()  # 해당 학교
    year = fields.IntField()  # 개설 년도
    term = fields.IntField()  # 개설 학기
    code = fields.StringField()  # 강의 코드
    type = fields.StringField()  # 과목 타입 (지교, 전필, 전선 등)
    subject_code = fields.StringField()     # 과목 코드
    subject_name = fields.StringField()     # 과목 이름
    credit = fields.IntField(default=0)  # 학점
    grade = fields.IntField(default=0)   # 기준 학년
    departments = fields.ListField(fields.StringField())
    professors = fields.ListField(fields.StringField())     # 담당 교수 리스트
    tags = fields.ListField(fields.StringField())   # e-러닝등 표시
    timetable_text = fields.StringField()   # 시간 텍스트
    timetable = fields.ListField(fields.EmbeddedDocumentField(LectureTime))
    email = fields.StringField()
    phone = fields.StringField()
    students = fields.ListField(fields.StringField())     # 수강생
    admins = fields.ListField(fields.ObjectIdField())

    meta = {
        'indexes': [
            {
                'fields': ['campus_id', '-year', '-term', 'code'],
                'unique': True
            },
            {
                'fields': ['students', '-year', '-term']
            },
            {
                'fields': ['admins', '-year', '-term']
            }
        ],
    }

    def get_term_text(self):
        if self.term == 1:
            return u'봄'
        if self.term == 2:
            return u'여름'
        if self.term == 3:
            return u'가을'
        if self.term == 4:
            return u'겨울'
        return u'(%d)' % self.term

    def get_term_str(self):
        return Lecture.term_int_to_str(self.term)

    def save(self, *args, **kwargs):
        Document.save(self, *args, **kwargs)
        searchengine.index(self)

    @staticmethod
    def search(campus_id, query, page, size=24, year=None, term=None):
        return searchengine.search(campus_id, query, page, size, year, term)

    @staticmethod
    def get_lecture(year, term, code):
        return Lecture.objects(year=year, term=Lecture.term_str_to_int(term), code=code).get()

    @staticmethod
    def term_int_to_str(term_int):
        if term_int == 1:
            return 'spring'
        elif term_int == 2:
            return 'summer'
        elif term_int == 3:
                return 'fall'
        elif term_int == 4:
            return 'winter'
        raise ValueError

    @staticmethod
    def term_str_to_int(term_str):
        if term_str == 'spring':
            return 1
        elif term_str == 'summer':
            return 2
        elif term_str == 'fall':
            return 3
        elif term_str == 'winter':
            return 4
        raise ValueError


class LectureAnalogue(Document):
    campus_id = fields.ObjectIdField()
    student_id = fields.StringField()
    point = fields.FloatField(default=0.0)
    target = fields.StringField()

    meta = {
        'indexes': [
            {
                'fields': ['campus_id', 'student_id'],
                'unique': True
            }
        ]
    }


class LectureBoard(Document):
    lecture_id = fields.ObjectIdField()
    board_id = fields.StringField()
    board_name = fields.StringField()
    read_perm = fields.StringField()
    write_perm = fields.StringField()

    meta = {
        'indexes': [
            {
                'fields': ['lecture_id', 'board_id'],
                'unique': True
            }
        ]
    }
