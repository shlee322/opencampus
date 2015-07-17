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

import json
from urllib import request, parse
from opencampus.server import app
from opencampus.gateway import methods
from opencampus.gateway.errors import GatewayError, get_error
from opencampus.gateway.queue import call_rpc_task


class GatewayItem():
    def __init__(self, gateway):
        from .encryptmanager import EncryptManager
        self._gateway = gateway
        self._encrypt_manager = EncryptManager(gateway.secret_key)

    def get_gateway(self):
        return self._gateway

    def get_encrypt_manager(self):
        return self._encrypt_manager


class Gateway():
    def __init__(self, campus):
        self.campus = campus
        self.gateway = {}
        self.apis = json.loads(campus.gateway_apis) if campus.gateway_apis else {}

    def _get_gateway_and_url(self, action):
        action = self.apis.get(action)
        if not action:
            return None, None

        gateway_id = action.get('gateway_id')
        gateway = self.gateway.get(gateway_id)
        if not gateway:
            from opencampus.common.models import CampusGateway
            try:
                gateway_obj = CampusGateway.objects(id=gateway_id, campus_id=self.campus.id).get()
            except CampusGateway.DoesNotExist:
                return None, None
            gateway = GatewayItem(gateway_obj)
            self.gateway[gateway_id] = gateway

        return gateway, action.get('url')

    def _call_rpc_task(self, action, data):
        if not (action in methods.GATEWAY_METHOD_IDS):
            raise Gateway(u'알 수 없는 게이트웨이 명령입니다. %s' % action)

        gateway, url = self._get_gateway_and_url(action)
        if not url:
            raise GatewayError(u'(캠퍼스매니저) 게이트웨이 %s API가 등록되어 있지 않습니다. 관리자에게 문의하여 주십시오.' % action)

        call_rpc_task.delay(url, gateway.get_encrypt_manager().encrypt(data), 60)

    def _call_rpc(self, action, data, deadline=10):
        if not (action in methods.GATEWAY_METHOD_IDS):
            raise Gateway(u'알 수 없는 게이트웨이 명령입니다. %s' % action)

        try:
            gateway, url = self._get_gateway_and_url(action)
            if not url:
                raise GatewayError(u'(캠퍼스매니저) 게이트웨이 %s API가 등록되어 있지 않습니다. 관리자에게 문의하여 주십시오.' % action)

            error = False
            result_data = {'error': {'code': ''}}
            try:
                result = request.urlopen(url, gateway.get_encrypt_manager().encrypt(data).encode('utf-8'), timeout=deadline).read()
            except request.HTTPError as e:
                error = True
                result = e.read()

            result = {key.decode('utf8'): value[0].decode('utf8') for (key, value) in parse.parse_qs(result).items()}
            result_data = gateway.get_encrypt_manager().decrypt(result)

            if error:
                raise get_error(result_data['error'])
        except Exception as e:
            if isinstance(e, GatewayError):
                raise e
            else:
                app.logger.exception(e)
                raise GatewayError(u'학교 게이트웨이와 통신 중 에러가 발생하였습니다. 잠시후 다시 시도해주세요.')

        return result_data

    def get_student_id(self, portal_id, portal_pw):
        """
        학교 학번을 받아오는 함수
        :param portal_id: 학교 포탈 ID
        :param portal_pw: 학교 포탈 PW
        :return: 학번 (student_id)
        """
        result = self._call_rpc(methods.METHOD_GET_STUDENT_ID, {
            'portal_id': portal_id,
            'portal_pw': portal_pw
        })

        if not result.get('student_id'):
            raise GatewayError(u'게이트웨이로부터 수신된 데이터가 올바르지 않습니다. 관리자에게 문의하여주십시오.')

        return result['student_id']

    def change_account_auth_info(self, data):
        """
        학생 정보를 저장하는 명령
        """
        self._call_rpc_task(methods.METHOD_CHANGE_ACCOUNT_AUTH_INFO, data)

    def delete_student_info(self, student_id):
        self._call_rpc_task(methods.METHOD_DELETE_STUDENT_INFO, {
            'student_id': student_id
        })

    """
    def sync_student_info(self, account):
        self._call_rpc_task(methods.METHOD_SYNC_STUDENT_INFO, {
            'student_id': account.student_id,
            'auth_data': account.get_campus_auth_data(),
        })
    """

    def sync_lecture(self, year, term, code):
        self._call_rpc_task(methods.METHOD_SYNC_LECTURE, {
            'year': year,
            'term': term,
            'code': code
        })

    def sync_student_lecture(self, account):
        self._call_rpc_task(methods.METHOD_SYNC_STUDENT_LECTURE, {
            'student_id': account.student_id,
            'auth_info': account.auth_info
        })

    def get_student_grade(self, account):
        result = self._call_rpc(methods.METHOD_GET_STUDENT_GRADE, {
            'student_id': account.student_id,
            'auth_info': account.auth_info
        })

        return result

    """
    def request_extension(self, obj):
        return self._call_rpc(methods.METHOD_REQUEST_EXTENSION, obj)
    """
