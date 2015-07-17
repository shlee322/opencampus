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

from flask import request, jsonify
from mongoengine.errors import NotUniqueError
from opencampus.common import modulemanager
from opencampus.common.models import Campus
from opencampus.module.lecture.models import Lecture, LectureTime


@modulemanager.api_route('lecture', '/v1/campuses/<string:campus_id>/lectures/create', methods=['POST'])
@modulemanager.gateway_only
def lecture_create(campus_id):
    try:
        request_data = request.get_json()
        year = request_data.get('year')
        term = Lecture.term_str_to_int(request_data.get('term'))
        code = request_data.get('code')
        if not (year and term and code):
            raise ValueError
    except TypeError or ValueError:
        return jsonify({'error': {'code': 'invalid_request'}})

    lecture = Lecture(
        campus_id=campus_id,
        year=year,
        term=term,
        code=code
    )
    try:
        lecture.save()
    except NotUniqueError:
        return jsonify({'error': {'code': 'lecture_exist'}}), 400
    return jsonify({
        'id': str(lecture.id),
        'year': year,
        'term': Lecture.term_int_to_str(lecture.term),
        'code': lecture.code
    })


@modulemanager.api_route('lecture',
                         '/v1/campuses/<string:campus_id>/lectures/<int:year>/<string:term>/<string:code>/update',
                         methods=['PUT'])
@modulemanager.gateway_only
def lecture_update(campus_id, year, term, code):
    try:
        lecture = Lecture.objects(campus_id=campus_id,
                                  year=year, term=Lecture.term_str_to_int(term), code=code).get()
    except Lecture.DoesNotExist:
        return jsonify({
            'error': {
                'code': 'lecture_not_exist'
            }
        }), 404
    request_data = request.get_json()

    lecture.type = request_data.get('type', lecture.type)
    lecture.subject_code = request_data.get('subject_code', lecture.subject_code)
    lecture.subject_name = request_data.get('subject_name', lecture.subject_name)
    lecture.credit = int(request_data.get('credit', lecture.credit))
    lecture.grade = int(request_data.get('grade', lecture.grade))
    lecture.departments = request_data.get('departments', lecture.departments)
    lecture.professors = request_data.get('professors', lecture.professors)
    lecture.tags = request_data.get('tags', lecture.tags)
    lecture.timetable_text = request_data.get('timetable_text', lecture.timetable_text)
    if request_data.get('timetable'):
        lecture.timetable = []
        for time in request_data.get('timetable'):
            lecture_time = LectureTime()
            if time.get('time'):
                lecture_time.start_time = time.get('time').get('start')
                lecture_time.end_time = time.get('time').get('end')
            if time.get('place'):
                lecture_time.place = time.get('place').get('name')
                lecture_time.room = time.get('place').get('room')

            lecture.timetable.append(lecture_time)

    lecture.email = request_data.get('email', lecture.email)
    lecture.phone = request_data.get('phone', lecture.phone)

    lecture.save()
    return jsonify({})


@modulemanager.api_route('lecture',
                         '/v1/campuses/<string:campus_id>/lectures/<int:year>/<string:term>/<string:code>/sync',
                         methods=['PUT'])
def lecture_sync(campus_id, year, term, code):
    try:
        lecture = Lecture.objects(campus_id=campus_id,
                                  year=year, term=Lecture.term_str_to_int(term), code=code).get()
    except Lecture.DoesNotExist:
        return jsonify({
            'error': {
                'code': 'lecture_not_exist'
            }
        }), 404

    campus = Campus.objects(id=campus_id).get()
    campus.get_gateway().sync_lecture(
        year=lecture.year,
        term=lecture.term_int_to_str(lecture.term),
        code=lecture.code
    )

    return jsonify({})


@modulemanager.api_route('lecture',
                         '/v1/campuses/<string:campus_id>/lectures/<int:year>/<string:term>/<string:code>/students',
                         methods=['POST'])
@modulemanager.gateway_only
def lecture_students(campus_id, year, term, code):
    try:
        lecture = Lecture.objects(campus_id=campus_id,
                                  year=year, term=Lecture.term_str_to_int(term), code=code).get()
    except Lecture.DoesNotExist:
        return jsonify({
            'error': {
                'code': 'lecture_not_exist'
            }
        }), 404

    request_data = request.get_json()
    student_id = request_data.get('student_id')

    # TODO
    """
    from opencampus.module.account.models import Account
    try:
        account = Account.objects(campus_id=request.campus.id, student_id=student_id).get()
    except Account.DoesNotExist:
        return jsonify({
            'error': {
                'code': 'account_not_found'
            }
        }), 404
    """

    #if account.id not in lecture.students:
    Lecture.objects(id=lecture.id).update_one(push__students=student_id)

    return jsonify({})


@modulemanager.api_route('lecture', '/v1/campuses/<string:campus_id>/lectures/search')
def lecture_search_api(campus_id):
    from urllib import parse

    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))

    data = Lecture.search(request.campus.id, query=query, page=page)

    for lecture in data:
        lecture['timetable'] = []
        try:
            lecture_data = Lecture.get_lecture(int(lecture['year']), lecture['term_str'], lecture['code'])
            for time in lecture_data.timetable:
                lecture['timetable'].append({
                    'place': time.place,
                    'room': time.room,
                    'start_time': time.start_time,
                    'end_time': time.end_time
                })
        except:
            pass

    result = {
        'data': data,
        'paging': {}
    }

    if len(data) >= 20:
        url = list(parse.urlparse(request.url))
        query = dict(parse.parse_qs(url[4]))
        query['page'] = page + 1
        url[4] = parse.urlencode(query)
        result['paging']['next'] = parse.urlunparse(url)

    return jsonify(result)
