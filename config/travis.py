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

import base64

DEBUG = True
SERVER_NAME = 'opencampus.dev:5000'
SECRET_KEY = base64.b64decode('zPhbPH6nIuaLNtb308+Z8msOSjs6TbPPrs/OWus5NWQ=')
SLACK_TOKEN = None

MONGODB_SETTINGS = {
    'host': '127.0.0.1',
    'db': 'opencampus-dev'
}

DEBUG_TB_PROFILER_ENABLED = True
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
DEBUG_TB_PANELS = ['flask.ext.mongoengine.panels.MongoDebugPanel']

DEVCONSOLE_GOOGLE_CLIENT_ID = ''
DEVCONSOLE_GOOGLE_CLIENT_SECRET = ''

DEVCONSOLE_SUPER_USERS = ['debug@opencampus.kr']
DEVCONSOLE_TEST_PROJECTS = []


GATEWAY_TASK_BROKER = 'redis://127.0.0.1:6379/0'
ELASTICSEARCH_HOSTS = [{'host': '127.0.0.1', 'port': 9200}]

DAUM_MAP_API_KEY = 'acfed97fedbf731d3adbf831e80949d5'

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_S3_BUCKET = ''

TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
