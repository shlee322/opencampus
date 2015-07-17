# Copyright (C) 2015 opencampus.kr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, ordfsdfasf
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import binascii
from Crypto import Random
from flask import request, session, abort
from opencampus.server import app


@app.before_request
def csrf_protect():
    if request.method == "POST":
        if request.host == 'apis.' + app.config.get('SERVER_NAME'):
            return
        token = session.get('csrf_token')
        if not token or token != request.form.get('csrf_token'):
            return abort(403)


def generate_csrf_token():
    if 'csrf_token' not in session:
        r = Random.new()
        session['csrf_token'] = str(binascii.hexlify(r.read(64)), 'utf-8')
    return session['csrf_token']


def generate_csrf_token_form():
    return "<input type='hidden' name='csrf_token' value='%s'/>" % generate_csrf_token()


app.jinja_env.globals['csrf_token'] = generate_csrf_token
app.jinja_env.globals['csrf_token_form'] = generate_csrf_token_form