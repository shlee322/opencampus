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

from flask import request, url_for
from opencampus.common.models import Campus
from opencampus.server import app


def get_campus():
    try:
        return Campus.objects(domain=request.host).get()
    except Campus.DoesNotExist:
        return None


def campus_url_builder(error, endpoint, values):
    if not endpoint.startswith('campus.'):
        return
    values.pop('_external', None)
    campus_domain = values.pop('campus_domain', None)
    if not campus_domain:
        campus_domain = str(request.campus.domain)

    url = url_for(endpoint[7:], _external=False, **values)
    return url.replace(app.config.get('SERVER_NAME'), campus_domain, 1)


app.url_build_error_handlers.append(campus_url_builder)
"""

def campus_url_for(endpoint, **values):
    return url_for(endpoint, **values)

app.jinja_env.globals['campus_url_for'] = campus_url_for
"""