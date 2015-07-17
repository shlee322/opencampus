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

from urllib import request
from celery import Celery
from opencampus.server import app
celery = Celery('gateway_task', broker=app.config.get('GATEWAY_TASK_BROKER'))


@celery.task(name='call_rpc_task', serializer='json')
def call_rpc_task(url, body, deadline):
    try:
        request.urlopen(url, body.encode('utf-8'), timeout=deadline).read()
    except request.HTTPError:
        pass
