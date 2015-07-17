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
from urllib.request import urlopen
from urllib.parse import urlencode
from flask import redirect, url_for, request, session, render_template
from opencampus.endpoint.developer.console.blueprint import console_blueprint
from opencampus.server import app


@console_blueprint.route('/console/login')
def login():
    if app.debug and not request.args.get('debug_use_oauth'):
        return render_template('developer/console/debug_login.html')

    oauth2_auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode({
        'scope': 'email',
        'redirect_uri': request.host_url[:-1] + url_for('console.login_cb'),
        'response_type': 'code',
        'client_id': app.config['DEVCONSOLE_GOOGLE_CLIENT_ID']
    })

    return redirect(oauth2_auth_url)


@console_blueprint.route('/console/login/cb')
def login_cb():
    email = None
    if app.debug and request.args.get('email'):
        email = request.args.get('email')
    else:
        token_res = urlopen('https://www.googleapis.com/oauth2/v3/token', urlencode({
            'code': request.args.get('code'),
            'redirect_uri': request.host_url[:-1] + url_for('console.login_cb'),
            'grant_type': 'authorization_code',
            'client_id': app.config['DEVCONSOLE_GOOGLE_CLIENT_ID'],
            'client_secret': app.config['DEVCONSOLE_GOOGLE_CLIENT_SECRET']
        }).encode('utf-8'))

        token_data = json.loads(token_res.read().decode('utf-8'))
        if not token_data.get('access_token'):
            return redirect(url_for('console.login'))

        user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo?access_token='
        user_info_res = urlopen(user_info_url + token_data.get('access_token'))
        user_info = json.loads(user_info_res.read().decode('utf-8'))

        if not user_info.get('verified_email'):
            return redirect(url_for('console.project_list'))

        email = user_info.get('email')

    session.set_admin_account(email)
    return redirect(url_for('console.project_list'))


@console_blueprint.route('/console/logout')
def logout():
    session.del_admin_account()
    return redirect(url_for('console.project_list'))