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
import jinja2
from flask import Flask, render_template, request, jsonify
from opencampus.load_modules import MODULE_NAMES, BLUEPRINTS

app = Flask(__name__, static_folder=None)
app.config.from_object(os.environ.get('OPENCAMPUS_SETTINGS', 'config.local'))
app.jinja_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader([
        os.path.join(os.path.dirname(__file__), '../templates/'),
        app.jinja_loader
    ])
])


if not app.debug:
    import logging
    from logging.handlers import SMTPHandler

    class OpenCampusErrorMailHandler(SMTPHandler):
        def emit(self, record):
            from opencampus.common.sendmail import send_email
            send_email(self.subject, self.format(record), self.toaddrs)

    mail_handler = OpenCampusErrorMailHandler('', 'support@opencampus.kr', ['dev@opencampus.kr'],
                                              'OpenCampus Error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(410)
@app.errorhandler(500)
def error_handler(e):
    if request.host.startswith('apis.'):
        return jsonify({'error': {'code': 'api_error'}}), e.code

    try:
        return render_template('error.html', error_code=e.code), e.code
    except Exception:
        return render_template('error.html', error_code=500), 500


def init_server():
    for module_name in MODULE_NAMES:
        __import__(module_name, globals(), locals(), ['*'])

    for blueprint in BLUEPRINTS:
        module, attr = blueprint.split(':')
        app.register_blueprint(getattr(__import__(module, fromlist=[attr]), attr))
