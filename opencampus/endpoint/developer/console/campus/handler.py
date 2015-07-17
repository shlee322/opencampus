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

import json
from functools import wraps
from flask import request, render_template, session, abort, redirect, url_for, jsonify
from opencampus.endpoint.developer.console.blueprint import console_blueprint
from opencampus.endpoint.developer.console.common import is_super_user
from opencampus.common.models import Campus, CampusGateway
from opencampus.common import modulemanager
from opencampus.gateway.methods import GATEWAY_METHOD_IDS
from opencampus.server import app
from opencampus.common.models import Campus


@console_blueprint.route('/console/campuses', methods=['GET'])
def campus_list():
    page = int(request.args.get('page', 1))
    projects = []

    if is_super_user():
        objects = Campus.objects.skip((page-1)*10).limit(10)
    else:
        objects = Campus.objects(admins__in=[session.get_admin_account()]).skip((page-1)*10).limit(10)

    for campus in objects:
            projects.append({
                'project_id': str(campus.id),
                'project_type': 'campus',
                'project_name': '%s%s %s' % (campus.univ_name, campus.univ_type, campus.campus_name)
            })

    if page != 1 and len(projects) < 1:
        return abort(404)

    return render_template('developer/console/main.html', projects=projects, view_create=is_super_user(),
                           next_page=page+1)


@console_blueprint.route('/console/campuses/create', methods=['GET', 'POST'])
def create_campus():
    if not session.get_admin_account() in app.config.get('DEVCONSOLE_SUPER_USERS', []):
        return abort(403)

    if request.method == 'POST':
        campus = Campus.create_campus(
            univ_name=request.form.get('univ_name'),
            univ_type=request.form.get('univ_type'),
            campus_name=request.form.get('campus_name'),
            admins=[session.get_admin_account()]
        )

        import opencampus.module.lecture.searchengine
        opencampus.module.lecture.searchengine.init_index(str(campus.id))

        return jsonify({
            'id': str(campus.id)
        })

    return render_template('developer/console/campus/create.html')


@console_blueprint.route('/console/campuses/create/init_index', methods=['POST'])
def init_campus_index():
    if not is_super_user():
        return abort(403)

    from elasticsearch import Elasticsearch
    es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))

    try:
        es.indices.close(index='campus_list')
    except:
        pass
    try:
        es.indices.put_settings(index='campus_list', body={
            "index": {
                "analysis": {
                    "analyzer": {
                        "korean": {
                            "type": "custom",
                            "tokenizer": "mecab_ko_standard_tokenizer"
                        }
                    }
                }
            }
        })
    except:
        es.indices.create(index='campus_list', body={
            "settings": {
                "index": {
                    "analysis": {
                        "analyzer": {
                            "korean": {
                                "type": "custom",
                                "tokenizer": "mecab_ko_standard_tokenizer"
                            }
                        }
                    }
                }
            }
        })

    es.indices.open(index='campus_list')

    try:
        es.indices.delete_mapping(index='campus_list', doc_type='campus')
    except:
        pass

    es.indices.put_mapping(index='campus_list', doc_type='campus', body={
        "_all": {
            "analyzer": "korean"
        }
    })

    return redirect(url_for('console.project_list'))


def campus_manager_func(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        campus_id = kwargs.get('campus_id')

        try:
            request.campus = Campus.objects(id=campus_id).get()
        except Campus.DoesNotExist:
            return abort(404)

        if not is_super_user() and session.get_admin_account() not in request.campus.admins:
            return abort(403)

        return f(*args, **kwargs)
    return decorated


@console_blueprint.route('/console/campuses/<string:campus_id>/')
@campus_manager_func
def campus_state(campus_id):
    return render_template('developer/console/campus/state.html',
                           campus=Campus.objects(id=campus_id).get(),
                           menu='state',
                           is_super_user=is_super_user(),
                           module_menus=modulemanager.get_manager_menus())


@console_blueprint.route('/console/campuses/<string:campus_id>/campus_id', methods=['POST'])
@campus_manager_func
def campus_save_state(campus_id):
    if not is_super_user():
        return abort(403)

    campus = Campus.objects(id=campus_id).get()
    campus.univ_name = request.form.get('univ_name')
    campus.domain = request.form.get('domain')
    campus.univ_type = request.form.get('univ_type')
    campus.campus_name = request.form.get('campus_name')
    campus.save()
    return redirect(url_for('console.campus_state', campus_id=campus_id))


@console_blueprint.route('/console/campuses/<string:campus_id>/gateways')
@campus_manager_func
def campus_gateways(campus_id):
    return render_template(
        'developer/console/campus/gateways.html',
        campus=Campus.objects(id=campus_id).get(),
        gateways=CampusGateway.objects(campus_id=campus_id),
        menu='gateways',
        gateway_method_ids=GATEWAY_METHOD_IDS,
        module_menus=modulemanager.get_manager_menus()
    )


@console_blueprint.route('/console/campuses/<string:campus_id>/gateways/add', methods=['POST'])
@campus_manager_func
def campus_add_gateway(campus_id):
    if CampusGateway.objects(campus_id=campus_id).count() > 2:
        return redirect(url_for('console.campus_gateways', campus_id=campus_id))

    CampusGateway.create_gateway(campus_id)
    return redirect(url_for('console.campus_gateways', campus_id=campus_id))


@console_blueprint.route('/console/campuses/<string:campus_id>/gateways/<string:gateway_id>', methods=['POST'])
@campus_manager_func
def campus_gateway_method(campus_id, gateway_id):
    gateway = CampusGateway.objects(id=gateway_id, campus_id=campus_id).get()

    if not gateway:
        return abort(404)

    if request.form.get('method') == 'reset_secret_key':
        gateway.reset_secret_key()
        gateway.save()
    elif request.form.get('method') == 'delete':
        gateway.delete()

    return redirect(url_for('console.campus_gateways', campus_id=campus_id))


@console_blueprint.route('/console/campuses/<string:campus_id>/gateways/save_apis', methods=['POST'])
@campus_manager_func
def campus_save_gateway_apis(campus_id):
    campus = Campus.objects(id=campus_id).get()
    apis = json.loads(campus.gateway_apis) if campus.gateway_apis else {}

    for method in GATEWAY_METHOD_IDS:
        gateway_id = request.form.get(method + '_gateway')
        url = request.form.get(method + '_url')
        try:
            gateway = CampusGateway.objects(id=gateway_id, campus_id=campus_id).get()
        except CampusGateway.DoesNotExist:
            return abort(400)

        apis[method] = {
            'gateway_id': gateway_id,
            'url': url
        }

    campus.gateway_apis = json.dumps(apis)
    campus.save()
    return redirect(url_for('console.campus_gateways', campus_id=campus_id))


@console_blueprint.route('/console/campuses/<string:campus_id>/menus', methods=['GET', 'POST'])
@campus_manager_func
def campus_menus(campus_id):
    if request.method == 'POST':
        menus = json.loads(request.form.get('menus'))
        request.campus.menus = json.dumps(menus)
        request.campus.save()

    def encode_menu(data):
        data = data.copy()
        del data['children']
        import json
        import urllib.parse
        return urllib.parse.quote(json.dumps(data).encode('utf-8'))

    return render_template(
        'developer/console/campus/menus.html',
        campus=Campus.objects(id=campus_id).get(),
        menu='menus',
        module_menus=modulemanager.get_manager_menus(),
        campus_service_menus=modulemanager.get_campus_service_menus(),
        encode_menu=encode_menu
    )
