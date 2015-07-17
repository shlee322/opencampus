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


class GatewayError(Exception):
    def __init__(self, message=None):
        self.message = message if message else u'서비스 점검 중 입니다'


class AuthPortalError(GatewayError):
    def __init__(self, message):
        GatewayError.__init__(self)
        self.message = message


class NotFoundPortalAccount(AuthPortalError):
    def __init__(self):
        AuthPortalError.__init__(self, u'포탈 아이디 혹은 비밀번호가 다릅니다')


def get_error(error):
    if error.get('code') == 'A0001':
        return NotFoundPortalAccount()

    return GatewayError(error)