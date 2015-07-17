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

import os
from flask import Blueprint, helpers, request, redirect

from opencampus.server import app

developer_blueprint = Blueprint('developer', __name__, subdomain='developers')

doc_dir = os.path.join(os.path.dirname(__file__), '../../../docs/_build/html')


@developer_blueprint.route('/_/invite_slack', methods=['GET'])
def invite_slack():
    slack_token = app.config.get('SLACK_TOKEN')
    if not slack_token:
        return redirect('/')

    form_fields = {
        "email": request.args.get('email'),
        "channels": app.config.get('SLACK_CHANNELS'),
        "token": slack_token,
        "set_active": "true"
    }

    import urllib.parse
    import urllib.request

    form_data = urllib.parse.urlencode(form_fields).encode('utf-8')
    req = urllib.request.Request('https://opencampus-kr.slack.com/api/users.admin.invite')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    res = urllib.request.urlopen(request, form_data)
    return redirect('/')


@developer_blueprint.route('/', methods=['GET'], defaults={'filename': 'index.html'})
@developer_blueprint.route('/<path:filename>', methods=['GET'])
def view_document(filename):
    return helpers.send_from_directory(doc_dir, filename)
