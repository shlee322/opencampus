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
from opencampus.server import app

app.static_folder = os.path.join(os.path.dirname(__file__), '../../../static')


@app.route('/<int:version>/<path:filename>', subdomain='static')
def static(version, filename):
    res = app.send_static_file(filename)
    res.headers['Cache-Control'] = 'max-age=86400, must-revalidate'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res
