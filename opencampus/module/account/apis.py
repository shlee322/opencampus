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

from flask import request, jsonify, abort
from opencampus.common import modulemanager
from opencampus.common.models import Campus
from opencampus.module.account.models import Account


@modulemanager.api_route('account', '/v1/accounts/me')
def account_me_info():
    if not request.access_token or request.access_token.access_obj_type != 'account':
        return jsonify({'error': {'code': 'not_found_account_access_token'}}), 403

    try:
        account = Account.objects(id=request.access_token.access_obj_id).id()
    except Account.DoesNotExist:
        return jsonify({'error': {'code': 'not_found_account'}}), 404

    info = {
    }

    if 'get_account' in request.access_token.scope:
        campus = Campus.objects(id=account.campus_id).get()
        info.update({
            'id': str(account.id),
            'campus': {
                'id': account.campus_id,
                'univ_name': campus.univ_name,
                'univ_type': campus.univ_type,
                'campus_name': campus.campus_name
            }
        })

    if 'get_student_id' in request.access_token.scope:
        info.update({
            'student_id': account.student_id
        })

    return jsonify(info)


@modulemanager.api_route('account', '/v1/accounts/me/grade')
def account_me_grade():
    if not request.access_token or request.access_token.access_obj_type != 'account':
        return jsonify({'error': {'code': 'not_found_account_access_token'}}), 403

    try:
        account = Account.objects(id=request.access_token.access_obj_id).get()
    except Account.DoesNotExist:
        return jsonify({'error': {'code': 'not_found_account'}}), 404

    if 'get_grade' not in request.access_token.scope:
        return jsonify({'error': {'code': 'error_scope'}}), 403

    campus = Campus.objects(id=account.campus_id).get()

    return jsonify({
        'data': campus.get_gateway().get_student_grade(account)
    })


@modulemanager.api_route('account', '/v1/account/change_campus_data', methods=['PUT'])
def account_change_auth_info():
    request_data = request.get_json()
    campus_id = request_data.get('campus_id')
    student_id = request_data.get('student_id')

    try:
        request.campus = Campus.objects(id=campus_id).get()
    except Campus.DoesNotExist:
        return jsonify({'error': {'code': 'not_found_campus'}}), 400

    @modulemanager.gateway_only
    def change_auth_info():
        try:
            account = Account.objects(campus_id=campus_id, student_id=student_id).get()
        except Account.DoesNotExist:
            return jsonify({'error': {'code': 'not_found_account'}}), 404

        if 'auth_info' in request_data:
            account.auth_info = request_data.get('auth_info')
        if 'name' in request_data:
            account.name = request_data.get('name')
        if 'departments' in request_data:
            account.departments = request_data.get('departments')
        account.save()
        return jsonify({'state': 'ok'})

    return change_auth_info()
