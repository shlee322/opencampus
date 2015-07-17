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

from datetime import datetime
from flask import request, render_template, abort, jsonify, redirect, url_for, session
from mongoengine import Q
from opencampus.common import modulemanager
from opencampus.module.lecture.models import Lecture, LectureBoard, LectureAnalogue
from opencampus.server import app


@modulemanager.campus_route('lecture', '/lectures/search', menu='강의 정보')
def lecture_search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    results = Lecture.search(request.campus.id, query=query, page=page)

    if page > 1 and len(results) < 1:
        return abort(404)

    return render_template('module/lecture/search.html', results=results, next_page=page+1, query=query)


@modulemanager.campus_route('lecture', '/lectures/my', menu='내 강의')
def lecture_my():
    if not session.get_account():
        return abort(403)

    lectures = []
    c_lectures = []
    year = -1
    term = -1

    for lecture in Lecture.objects(Q(students__in=[session.get_account().student_id]) | Q(admins__in=[session.get_account().id])).\
            order_by('-year', '-term'):
        if lecture.year != year or lecture.term != term:
            lectures.append(c_lectures)
            c_lectures = []
            year = lecture.year
            term = lecture.term
        c_lectures.append(lecture)
    lectures.append(c_lectures)

    lectures = lectures[1:]
    return render_template('module/lecture/my.html', lectures=lectures)


@modulemanager.campus_route('lecture', '/lectures/my/sync', methods=['POST'])
def lecture_my_sync_lecture():
    if not session.get_account():
        return abort(403)

    request.campus.get_gateway().sync_student_lecture(session.get_account())
    return redirect(url_for('campus.lecture_my'))


@modulemanager.campus_route('lecture', '/lectures/vtimetable', menu='모의시간표')
def lecture_vtimetable():
    current_year = datetime.now().year
    recommend = []

    if session.get_account():
        try:
            analogue = LectureAnalogue.objects(
                campus_id=session.get_account().campus_id,
                student_id=session.get_account().student_id
            ).get()

            lectures1 = Lecture.objects(students__in=[session.get_account().student_id])
            lectures2 = Lecture.objects(students__in=[analogue.target])

            lectures1 = set([l.subject_code for l in lectures1])
            lectures2 = set([l.subject_code for l in lectures2])

            lectures = lectures2 - lectures1
            
            for lecture in lectures:
                try:
                    lecture = Lecture.objects(subject_code=lecture)[0]
                    recommend.append(lecture.subject_name)
                except:
                    pass
        except:
            pass

    return render_template('module/lecture/vtimetable.html', current_year=current_year, recommend=recommend)


@modulemanager.campus_route('lecture', '/lectures/vtimetable/search')
def lecture_vtimetable_search():
    try:
        year = int(request.args.get('year'))
        term = Lecture.term_str_to_int(request.args.get('term'))
        query = request.args.get('q', '')
    except TypeError:
        return jsonify({'error': {'code': 'type_error'}}), 400

    results = Lecture.search(request.campus.id, query=query, page=1, size=8, year=year, term=term)

    for lecture in results:
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

    return jsonify({
        'data': results
    })


@modulemanager.campus_route('lecture', '/lectures/vacancy', menu='빈 강의실 조회')
def lecture_vacancy():
    year = 2015
    term = 1
    weekday = 0
    current_time = 60*60*13

    map_f = """
    function() {
        if(this.campus_id != '%s' || this.year != %d || this.term != %d) return;
        for(var i=0; i<this.timetable.length; i++) {
            if(this.timetable[i].start_time < %d || this.timetable[i].start_time >= %d) continue;
            emit(this.timetable[i].place+'_'+this.timetable[i].room, {time_info:this.timetable[i], lecture:this});
        }
    }
    """ % (request.campus.id, year, term, weekday*86400, (weekday+1)*86400)

    reduce_f = """
    function(key, values) {
        var pre_lecture_info = null;
        var next_lecture_info = null;

        for(var i=0; i<values.length; i++) {
            var lecture = values[i];
            if(lecture.time_info.start_time <= %d && (pre_lecture_info == null || lecture.time_info.start_time > pre_lecture_info.time_info.start_time)) {
                pre_lecture_info = lecture;
            }
            if(lecture.time_info.end_time >= %d && (next_lecture_info == null || lecture.time_info.end_time < next_lecture_info.time_info.end_time)) {
                next_lecture_info = lecture;
            }
        }
        if(pre_lecture_info && pre_lecture_info.time_info.end_time > %s) return {};
        if(next_lecture_info && next_lecture_info.time_info.start_time < %s) return {};
        return {'pre':pre_lecture_info, next:next_lecture_info};
    }
    """ % (current_time, current_time, current_time, current_time)

    places = []
    place_timetable = Lecture.objects.map_reduce(map_f, reduce_f, 'lecture_vacancy')
    for place in place_timetable:
        pre_lecture = place.value.get('pre')
        next_lecture = place.value.get('next')
        if not pre_lecture and not next_lecture:
            continue

        place_info = (pre_lecture if pre_lecture else next_lecture).get('time_info')
        vacancy_start = pre_lecture.get('time_info').get('end_time') if pre_lecture else weekday*86400
        vacancy_end = next_lecture.get('time_info').get('start_time') if next_lecture else (weekday+1)*86400


        #print(place_info.get('place'), place_info.get('room'), ' ', vacancy_start, ' ~ ', vacancy_end)

        #print(pre_lecture.get('time_info'))
        #next_lecture.get('time_info')

    return render_template('module/lecture/my.html')



@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/sync', methods=['POST'])
def lecture_sync(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)
    request.campus.get_gateway().sync_lecture(
        year=lecture.year,
        term=lecture.term_int_to_str(lecture.term),
        code=lecture.code
    )
    return redirect(url_for('campus.lecture_detail', year=year, term=term, code=code))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>')
def lecture_detail(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)
    from opencampus.module.place.models import Place
    places = Place.objects(campus_id=request.campus.id, names__in=[time_info.place for time_info in lecture.timetable])
    return render_template('module/lecture/detail/information.html', year=year, term=term, code=code,
                           lecture=lecture, places=places)


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/boards')
def lecture_board(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)
    boards = LectureBoard.objects(lecture_id=lecture.id)
    if len(lecture.admins) < 1:
        return redirect(url_for('campus.lecture_auth_admin', year=year, term=term, code=code))

    if len(boards) < 1:
        return redirect(url_for('campus.lecture_admin_board', year=year, term=term, code=code))

    return redirect(url_for('campus.lecture_board_list', year=year, term=term, code=code, board_id=boards[0].board_id))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/boards/<string:board_id>/')
def lecture_board_list(year, term, code, board_id):
    lecture = Lecture.get_lecture(year, term, code)
    boards = LectureBoard.objects(lecture_id=lecture.id)
    board = LectureBoard.objects(lecture_id=lecture.id, board_id=board_id).get()

    return render_template('module/lecture/detail/board.html', year=year, term=term, code=code,
                           lecture=lecture, boards=boards, board=board)


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/boards/<int:article_id>')
def lecture_board_show_article(year, term, code, article_id):
    return render_template('module/lecture/detail/article.html', year=year, term=term, code=code,
                           lecture=Lecture.get_lecture(year, term, code), article_id=article_id)

@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/boards/<string:board_id>/write')
def lecture_board_write(year, term, code, board_id):
    return render_template('module/lecture/detail/write_article.html', year=year, term=term, code=code,
                           lecture=Lecture.get_lecture(year, term, code))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/homework')
def lecture_homework(year, term, code):
    return render_template('module/lecture/detail/homework.html', year=year, term=term, code=code,
                           lecture=Lecture.get_lecture(year, term, code))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/attendance')
def lecture_attendance(year, term, code):
    return render_template('module/lecture/detail/attendance.html', year=year, term=term, code=code,
                           lecture=Lecture.get_lecture(year, term, code))


def admin_only(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        lecture = Lecture.get_lecture(kwargs.get('year', None), kwargs.get('term', None), kwargs.get('code', None))
        if session.get_account().id not in lecture.admins:
            return abort(403)

        return f(*args, **kwargs)

    return decorated


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/admin')
@admin_only
def lecture_admin(year, term, code):
    return redirect(url_for('campus.lecture_admin_board', year=year, term=term, code=code))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/admin/board')
@admin_only
def lecture_admin_board(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)
    return render_template('module/lecture/detail/admin/board.html', year=year, term=term, code=code,
                           lecture=lecture, boards=LectureBoard.objects(lecture_id=lecture.id))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/admin/board/create',
                            methods=['POST'])
@admin_only
def lecture_admin_board_create(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)

    try:
        board = LectureBoard.objects(lecture_id=lecture.id, board_id=request.form.get('board_id')).get()
    except LectureBoard.DoesNotExist:
        board = LectureBoard()

    board.lecture_id = lecture.id
    board.board_id = request.form.get('board_id')
    board.board_name = request.form.get('board_name')
    board.read_perm = request.form.get('read_perm')
    board.write_perm = request.form.get('write_perm')
    board.save()
    return jsonify({})



@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/admin/grade')
@admin_only
def lecture_admin_grade(year, term, code):
    return render_template('module/lecture/detail/admin/grade.html', year=year, term=term, code=code,
                           lecture=Lecture.get_lecture(year, term, code))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/admin/administrators',
                            methods=['GET', 'POST'])
@admin_only
def lecture_admin_administrators(year, term, code):
    from opencampus.module.account.models import Account
    lecture = Lecture.get_lecture(year, term, code)

    if request.method == 'POST':
        try:
            account = Account.objects(account_id=request.form.get('account_id')).get()
            if account.id not in lecture.admins:
                Lecture.objects(id=lecture.id).update_one(push__admins=account.id)
        except Account.DoesNotExist:
            pass

        lecture = Lecture.get_lecture(year, term, code)

    admins = [Account.objects(id=admin).get() for admin in lecture.admins]

    return render_template('module/lecture/detail/admin/administrators.html', year=year, term=term, code=code,
                           lecture=lecture, admins=admins)


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/admin/administrators/remove',
                            methods=['POST'])
@admin_only
def lecture_admin_administrators_remove(year, term, code):
    from opencampus.module.account.models import Account
    account = Account.objects(account_id=request.form.get('account_id')).get()
    lecture = Lecture.get_lecture(year, term, code)
    Lecture.objects(id=lecture.id).update_one(pull__admins=account.id)
    return redirect(url_for('campus.lecture_admin_administrators', year=year, term=term, code=code))


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/auth_admin')
def lecture_auth_admin(year, term, code):
    # TODO : Remove
    lecture = Lecture.get_lecture(year, term, code)
    lecture.email = 'shlee322@gmail.com'
    lecture.phone = '+821051277004'

    return render_template('module/lecture/detail/auth_admin.html', year=year, term=term, code=code,
                           lecture=lecture)


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/lecture_auth_admin_method',
                            methods=['POST'])
def lecture_auth_admin_method(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)

    # TODO : Remove
    lecture.email = 'shlee322@gmail.com'
    lecture.phone = '+821051277004'

    if not session.get_account():
        return '<p>로그인 후 사용해주세요</p>'

    from opencampus.module.lecture.authmodels import LectureAuthRequestInfo

    if request.form.get('type') == 'email':
        if not lecture.email:
            return '강의정보에 이메일이 등록되어 있지 않습니다'

        at_index = lecture.email.find('@')

        email_view = '*' * (at_index-3) + lecture.email[at_index-3:]
        if at_index < 3:
            email_view = '*' * at_index + lecture.email[at_index:]

        try:
            from opencampus.common.sendmail import send_email
            send_email('[오픈캠퍼스] 관리자 인증 메일 - %s년 %s학기 %s(%s)' % (lecture.year, lecture.get_term_text(),
                                                                lecture.code, lecture.subject_name),
                       render_template('module/lecture/detail/sendemail.html', lecture=lecture,
                                       auth_code=LectureAuthRequestInfo.create_request(lecture.id, 'email', session.get_account().id)),
                       [lecture.email])
        except Exception as e:
            print(e)
            return '<p>메일 발송 도중 에러가 발생하였습니다</p>'

        return '<p>%s으로 이메일이 발송되었습니다.</p><p>이메일에 기재되어 있는 방법을 이용하여 인증을 진행하여 주십시오.</p>' % email_view

    if request.form.get('type') == 'ars':
        if not lecture.phone:
            return '강의정보에 전화번호가 등록되어 있지 않습니다'

        phone_view = lecture.phone[:7] + '*' * (len(lecture.phone) - 7)
        body = '<p>%s으로 ARS가 발송되었습니다.</p><p>전화를 받으신 후 아래의 인증코드를 입력하신후 # 버튼을 눌러주세요.</p>' % phone_view
        body += '<div class="well well-sm"><h2>3333</h2></div>'
        return body
    if request.form.get('type') == 'sms':
        if not lecture.phone:
            return '강의정보에 전화번호가 등록되어 있지 않거나 휴대폰 번호가 아닙니다'

        phone_view = lecture.phone[:7] + '*' * (len(lecture.phone) - 7)

        auth_code = LectureAuthRequestInfo.create_request(lecture.id, 'sms', session.get_account().id)

        from twilio.rest import TwilioRestClient
        account_sid = app.config.get('TWILIO_ACCOUNT_SID')
        auth_token = app.config.get('TWILIO_AUTH_TOKEN')
        client = TwilioRestClient(account_sid, auth_token)
        message = client.messages.create(body="[오픈캠퍼스 인증] 인증번호 %s" % auth_code,
                                         to=lecture.phone,
                                         from_="+18559731333")

        body = '<p>%s으로 SMS가 발송되었습니다.</p><p>수신된 인증코드를 입력하여 주시기 바랍니다.</p>' % phone_view
        body += '<form action="%s" method="GET">' % url_for('campus.lecture_auth_admin_method_cb', year=year, term=term, code=code)
        body += '<input type="number" name="auth_code" class="form-control input-lg" placeholder="인증번호">'
        body += '<button type="submit" class="btn btn-danger btn-lg">인증</button>'
        body += '</form>'
        return body
    if request.form.get('type') == 'manual':
        body = '<p>해당 강의 정보와 관리자임을 증빙 할 수 있는 서류 등을 첨부하여</p>'
        body += '<p><a href="mailto:support@opencampus.kr">support@opencampus.kr</a>로 보내주시기 바랍니다.</p>'
        return body

    return '비정상 접근'


@modulemanager.campus_route('lecture', '/lectures/<int:year>/<string:term>/<string:code>/lecture_auth_admin_method_cb',
                            methods=['GET', 'POST'])
def lecture_auth_admin_method_cb(year, term, code):
    lecture = Lecture.get_lecture(year, term, code)
    from opencampus.module.lecture.authmodels import LectureAuthRequestInfo
    request_info = LectureAuthRequestInfo.objects(lecture_id=lecture.id, auth_code=request.args.get('auth_code')).get()
    request_info.delete()
    Lecture.objects(id=lecture.id).update_one(push__admins=request_info.account_id)
    return '인증 완료'


@modulemanager.campus_route('lecture', '/lecture/review')
def lecture_review():
    return render_template('module/lecture/review/main.html')
