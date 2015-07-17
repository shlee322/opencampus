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

from urllib import parse
from flask import request, jsonify
from opencampus.common import modulemanager
from opencampus.common.campus import Campus


@modulemanager.api_route('campus', '/v1/campuses', methods=['GET'])
def campus_search():
    query = request.args.get('q')
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    data = []

    if not query:
        campuses = Campus.objects().skip(skip).limit(limit)
    else:
        campuses = []

    for campus in campuses:
        campus_data = {
            'id': str(campus.id),
            'university': {
                'name': campus.univ_name,
                'type': campus.univ_type
            },
            'campus': {
                'name': campus.campus_name
            }
        }
        if campus.domain:
            campus_data['domain'] = campus.domain

        data.append(campus_data)

    result = {
        'data': data,
        'paging': {}
    }

    if skip > 0:
        url = list(parse.urlparse(request.url))
        query = dict(parse.parse_qs(url[4]))
        query['skip'] = skip - limit
        query['limit'] = limit
        if query['skip'] < 0:
            query['skip'] = 0
        url[4] = parse.urlencode(query)
        result['paging']['previous'] = parse.urlunparse(url)

    if len(data) >= limit:
        url = list(parse.urlparse(request.url))
        query = dict(parse.parse_qs(url[4]))
        query['skip'] = skip + len(data)
        query['limit'] = limit
        url[4] = parse.urlencode(query)
        result['paging']['next'] = parse.urlunparse(url)

    return jsonify(result)
