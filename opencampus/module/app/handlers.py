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

from elasticsearch import Elasticsearch
from flask import request, render_template, abort, jsonify, redirect, url_for, session
from opencampus.server import app
from opencampus.common import modulemanager
from opencampus.common.models import Application, ApplicationEmbedded


@modulemanager.campus_route('app', '/apps/search', menu='Apps')
def app_search():
    query = request.args.get('q', '')
    page = int(request.args.get('page', 1)) - 1
    size = 20
    results = []

    if query == '':
        results = [Application.objects(id=embedded.application_id).get() for embedded in ApplicationEmbedded.objects(
            campus_ids__in=[request.campus.id]).skip(page*size).limit(size)]
    else:
        es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))

        search_body = {
            'from': page*size,
            'size': size,
            'sort': ['_score'],
            'query': {
                'bool': {
                    'must': [
                        {
                            'term': {
                                'embedded_app.campus_ids': str(request.campus.id)
                            }
                        },
                        {
                            'query_string': {
                                "default_field": "_all",
                                "query": query
                            }
                        }
                    ]
                }
            }
        }

        res = es.search(index='embedded_app_list', body=search_body)

        for result_app in res.get('hits').get('hits'):
            results.append({
                'id': result_app.get('_source').get('app_id'),
                'name': result_app.get('_source').get('name'),
                'description': result_app.get('_source').get('description'),
            })

    if page > 1 and len(results) < 1:
        return abort(404)

    return render_template('module/app/search.html', results=results, next_page=page+2, query=query)


@modulemanager.campus_route('app', '/apps/<string:app_id>')
def app_run(app_id):
    try:
        embeded = ApplicationEmbedded.objects(application_id=app_id).get()
    except ApplicationEmbedded.DostNotFound:
        return abort(404)

    return render_template('module/app/run.html', embeded=embeded)
