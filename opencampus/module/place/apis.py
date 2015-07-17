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
from opencampus.module.place.models import Place


@modulemanager.api_route('place', '/v1/campuses/<string:campus_id>/places', methods=['GET'])
def place_search(campus_id):
    query = request.args.get('q')
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    data = []

    if not query:
        places = Place.objects(campus_id=campus_id)
    else:
        places = Place.objects(campus_id=campus_id, names__in=[query])

    places = places.skip(skip).limit(limit)

    for place in places:
        data.append({
            'id': str(place.id),
            'names': place.names,
            'location': {
                'latitude': place.location[0],
                'longitude': place.location[1]
            }
        })

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
