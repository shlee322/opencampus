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

from mongoengine import Q

MODULE_NAMES = [
    'opencampus.common.db',
    'opencampus.common.session',
    'opencampus.common.csrf',
    'opencampus.endpoint.static',
    'opencampus.endpoint.developer.views',
    'opencampus.endpoint.developer.console.blueprint',

    # Campus Site Module
    'opencampus.module.account.apis',
    'opencampus.module.account.handlers',
    'opencampus.module.app.apis',
    'opencampus.module.app.handlers',
    'opencampus.module.campus.apis',
    'opencampus.module.lecture.apis',
    'opencampus.module.lecture.handlers',
    'opencampus.module.lecture.manager',
    'opencampus.module.main.handlers',
    'opencampus.module.place.apis',
    'opencampus.module.place.manager',
    'opencampus.module.wiki.handlers',
]

BLUEPRINTS = [
    'opencampus.endpoint.developer.views:developer_blueprint',
    'opencampus.endpoint.developer.console.blueprint:console_blueprint',
    'opencampus.endpoint.api.blueprint:api_blueprint',

    # Campus blueprint는 별도처리
]
