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

from flask import request, render_template, abort, jsonify, redirect, url_for, session
from mongoengine.errors import NotUniqueError
from opencampus.common import modulemanager
from opencampus.gateway.errors import NotFoundPortalAccount
from opencampus.module.account.models import Account
from opencampus.module.account.errors import AccountNotFound, DoesNotMatchPassword


@modulemanager.campus_route('account', '/account/login', methods=['POST'])
def account_login():
    account_id = request.form.get('account_id')
    account_pw = request.form.get('account_pw')

    try:
        Account.login(account_id, account_pw)
    except AccountNotFound:
        return jsonify({'error': {'code': 'account_not_found'}}), 404
    except DoesNotMatchPassword:
        return jsonify({'error': {'code': 'does_not_match_password'}}), 403

    return jsonify({})

@modulemanager.campus_route('account', '/account/logout', methods=['POST'])
def account_logout():
    if not session.get_account():
        return abort(403)
    session.del_account(session.get_account())
    return redirect('/')


@modulemanager.campus_route('account', '/account/mypage')
def account_mypage():
    if not session.get_account():
        return abort(403)

    return render_template('module/account/information.html')


@modulemanager.campus_route('account', '/account/join', methods=['GET', 'POST'])
def account_join():
    if request.method == 'GET':
        # TODO : move privacy_policy.txt
        privacy_policy = """수집하는 개인정보의 항목
오픈캠퍼스는 회원가입, 각종 서비스 등 기본적인 서비스 제공을 위한 필수정보와 고객 맞춤 서비스 제공을 위한 선택정보로 구분하여 아래와 같은 개인정보를 수집하고 있습니다.

1) 회원가입 / 본인인증을 위한 수집
필수항목 : 아이디, 비밀번호, 재학중인 학교, 학번, 학교 포탈 인증 정보

2) 서비스 제공을 위한 수집
필수항목 : 재학중인 학과, 수강신청 내역 등의 학교 포탈에 등록된 본인과 관련된 정보

3) 쿨하우스 연동 시
필수항목 : 쿨하우스 입주생 인증 정보

4) 서비스 이용 과정에서 아래와 같은 정보들이 자동으로 생성되어 수집될 수 있습니다.
IP Address, 쿠키, 방문 일시, 서비스 이용 기록, 불량 이용 기록, 기기정보

5) Google Analytics
사용하는 브라우저, 접속지역, 해상도, 운영체제 정보등이 수집되며 자세한 사항은 Google Analytics의 관련 페이지에서 확인할 수 있습니다.
또한 유저별 데이터 분석을 위해 Google Analytics User-ID 정책 따라 사용자 고유식별번호가 수집될 수 있습니다.

선택정보를 입력하지 않은 경우에도 서비스 이용 제한은 없으며 이용자의 기본적 인권 침해의 우려가 있는 민감한 개인 정보(인종, 사상 및 신조, 정치적 성향 이나 범죄기록, 의료정보 등)는 기본적으로 수집하지 않습니다.
다만 불가피하게 수집이 필요한 경우 반드시 사전에 동의 절차를 거치도록 하겠습니다.

개인정보의 수집 • 이용목적
오픈캠퍼스는 이용자의 소중한 개인정보를 다음과 같은 목적으로만 이용하며, 목적이 변경될 경우에는 '개인정보취급방침의 변경' 항목에 따라 고지됩니다.
회원으로 가입한 이용자를 식별하고 가입의사, 불량회원의 부정한 이용을 방지하기 위하여 사용합니다.
이용자에게 오픈캠퍼스의 다양한 서비스를 제공하고 서비스 이용 과정에서 이용자의 문의사항이나 불만을 처리하고 공지사항 등을 전달하기 위해 사용합니다.
이용자와 약속한 서비스를 제공하고 유료 서비스 구매 및 이용이 이루어지는 경우 이에 따른 요금 정산을 위해 사용됩니다.
신규 서비스가 개발되거나 이벤트 행사 시 참여기회를 알리기 위한 정보 전달 및 마케팅 및 광고 등에도 사용됩니다.
이용자의 서비스 이용 기록과 접속 빈도 분석 및 서비스 이용에 대한 통계, 이를 통한 맞춤형 서비스 제공과 서비스 개선에도 사용됩니다.

개인정보의 보유 • 이용기간
오픈캠퍼스는 이용자의 개인정보를 회원가입을 하는 시점부터 서비스를 제공하는 기간 동안에만 제한적으로 이용하고 있습니다. 이용자가 회원탈퇴를 요청하거나 제공한 개인정보의 수집 및 이용에 대한 동의를 철회하는 경우, 또는 수집 및 이용목적이 달성되거나 보유 및 이용기간이 종료한 경우 해당 이용자의 개인정보는 지체 없이 파기 됩니다.
그리고 관계법령의 규정에 따라 아래와 같이 관계 법령에서 정한 일정한 기간 동안 회원정보를 보관합니다.

서비스 이용 관련 개인정보 (접근 기록)
보존 근거 : 통신비밀보호법 보존 기간 : 3개월
        """
        return render_template('module/account/join/terms.html', privacy_policy=privacy_policy)

    # Ajax
    phase = request.form.get('phase')

    if phase == 'choice_auth':
        return render_template('module/account/join/choice_auth.html')

    elif phase == 'auth_portal':
        return render_template('module/account/join/auth_portal.html')

    elif phase == 'req_auth_portal':
        portal_id = request.form.get('portal_id')
        portal_pw = request.form.get('portal_pw')
        if not portal_id or not portal_pw:
            return render_template('module/account/join/auth_portal.html',
                                   req_auth=True, portal_id=portal_id, portal_pw=portal_pw)

        try:
            student_id = request.campus.get_gateway().get_student_id(portal_id, portal_pw)
            try:
                Account.objects(campus_id=request.campus.id, student_id=student_id).get()
                return render_template('module/account/join/auth_portal.html',
                                       req_auth=True, portal_id=portal_id, portal_pw=portal_pw,
                                       error='이미 회원가입되어있는 사용자입니다. 아이디 비밀번호 찾기를 이용해주세요.')
            except Account.DoesNotExist:
                pass

            session['join_req_data'] = {
                'type': 'auth_portal',
                'portal_id': portal_id,
                'portal_pw': portal_pw,
                'student_id': student_id
            }

            return render_template('module/account/join/join_form.html',
                                   portal_id=portal_id, portal_pw=portal_pw)

        except NotFoundPortalAccount:
            return render_template('module/account/join/auth_portal.html',
                                   req_auth=True, portal_id=portal_id, portal_pw=portal_pw,
                                   error='아이디 혹은 비밀번호가 다릅니다')
        except:
            return render_template('module/account/join/auth_portal.html',
                                   req_auth=True, portal_id=portal_id, portal_pw=portal_pw,
                                   error='포탈 서버와 통신 중 장애가 발생하였습니다. 신속히 해결하도록 하겠습니다.')

    elif phase == 'req_join':
        account_id = request.form.get('account_id')
        account_pw = request.form.get('account_pw')
        account_nick = request.form.get('account_nick')

        if not account_id or not account_pw or not account_nick:
            return render_template('module/account/join/join_form.html',
                                   error='잘못된 입력값',
                                   account_id=account_id, account_pw=account_pw, account_nick=account_nick)

        if not Account.valid_account_id(account_id):
            return render_template('module/account/join/join_form.html',
                                   error='아이디는 6~30자의 영문소문자, 숫자, -, _로 이루어져야 하며 영문 소문자로 시작되어야 합니다.',
                                   account_id=account_id, account_pw=account_pw, account_nick=account_nick)

        if not Account.valid_account_pw(account_pw):
            return render_template('module/account/join/join_form.html',
                                   error='비밀번호는 영문, 숫자, 특수문자를 조합하여 8자리 이상이여야합니다.',
                                   account_id=account_id, account_pw=account_pw, account_nick=account_nick)

        if not Account.valid_nickname(account_nick):
            return render_template('module/account/join/join_form.html',
                                   error='닉네임은 3~10자로 지정하여야 합니다.',
                                   account_id=account_id, account_pw=account_pw, account_nick=account_nick)

        if not session['join_req_data'] or not session['join_req_data']['student_id']:
            abort(403)

        try:
            Account.create_account(
                campus_id=request.campus.id,
                account_id=account_id,
                account_pw=account_pw,
                nickname=account_nick,
                account_type='default',
                student_id=session['join_req_data']['student_id']
            )

            request.campus.get_gateway().change_account_auth_info(session['join_req_data'])

            del session['join_req_data']
        except NotUniqueError:
            return render_template('module/account/join/join_form.html',
                                   error='이미 존재하는 아이디입니다.')

        return '<script type="text/javascript"> location.href="/"; </script>'

@modulemanager.campus_route('account', '/account/find', methods=['GET', 'POST'])
def account_find():

    if request.method == 'GET':
        return render_template('module/account/find/choice_auth.html')

    phase = request.form.get('phase')

    if phase == 'portal_id':
        return render_template('module/account/find/portal_id_auth.html')
    elif phase == 'email':
        return render_template('module/account/find/portal_id_auth.html')
    elif phase == 'req_auth_portal':

        # TODO : 포탈 인증 & DB에서 계정정보 가져오는것 구현해줘요!

        portal_id = request.form.get('portal_id')
        portal_pw = request.form.get('portal_pw')

        return render_template('module/account/find/new_pw.html', portal_id=portal_id)
