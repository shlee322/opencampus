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

from datetime import datetime
from functools import wraps
from flask import render_template, session, abort, redirect, url_for, request
from opencampus.endpoint.developer.console.blueprint import console_blueprint
from opencampus.endpoint.developer.console.common import is_super_user
from opencampus.common import storage
from opencampus.common.models import Application, ApplicationOAuth2Client, Campus, ApplicationEmbedded
from opencampus.server import app


@console_blueprint.route('/console/apps')
def app_list():
    page = int(request.args.get('page', 1))
    projects = []

    if is_super_user():
        objects = Application.objects.skip((page-1)*10).limit(10)
    else:
        objects = Application.objects(admins__in=[session.get_admin_account()]).skip((page-1)*10).limit(10)

    for app in objects:
        projects.append({
            'project_id': str(app.id),
            'project_type': 'app',
            'project_name': '%s' % app.name
        })

    if page != 1 and len(projects) < 1:
        return abort(404)

    return render_template('developer/console/main.html', projects=projects, view_create=True,
                           next_page=page+1)


@console_blueprint.route('/console/apps/create', methods=['GET', 'POST'])
def create_app():
    if not session.get_admin_account():
        return abort(403)

    if request.method == 'POST':
        application = Application()
        application.name = request.form.get('app_name')
        application.created_at = datetime.utcnow()
        application.admins = [session.get_admin_account()]
        application.save()

        return redirect(url_for('console.app_state', app_id=application.id))

    return render_template('developer/console/app/create.html', is_super_user=is_super_user())


@console_blueprint.route('/console/apps/create/init_index', methods=['POST'])
def init_app_index():
    if not is_super_user():
        return abort(403)

    from elasticsearch import Elasticsearch
    es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))

    try:
        es.indices.close(index='embedded_app_list')
    except:
        pass
    try:
        es.indices.put_settings(index='embedded_app_list', body={
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
        es.indices.create(index='embedded_app_list', body={
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

    es.indices.open(index='embedded_app_list')

    try:
        es.indices.delete_mapping(index='embedded_app_list', doc_type='embedded_app')
    except:
        pass

    es.indices.put_mapping(index='embedded_app_list', doc_type='embedded_app', body={
        "_all": {
            "analyzer": "korean"
        }
    })

    return redirect(url_for('console.project_list'))


def app_manager_func(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        app_id = kwargs.get('app_id')

        try:
            request.app = Application.objects(id=app_id).get()
        except Application.DoesNotExist:
            return abort(404)

        if not is_super_user() and session.get_admin_account() not in request.app.admins:
            return abort(403)

        return f(*args, **kwargs)
    return decorated


@console_blueprint.route('/console/apps/<string:app_id>/', methods=['GET', 'POST'])
@app_manager_func
def app_state(app_id):
    if request.method == 'POST':
        request.app.name = request.form.get('app_name')
        request.app.description = request.form.get('description')
        request.app.save()
        if request.files.get('image') and request.files.get('image').content_type.startswith('image/'):
            storage.put('/apps/images/%s' % request.app.id, request.files.get('image'))

    return render_template('developer/console/app/state.html')


@console_blueprint.route('/console/apps/<string:app_id>/oauth2', methods=['GET'])
@app_manager_func
def app_oauth2(app_id):
    oauth2_clients = ApplicationOAuth2Client.objects(application_id=request.app.id)
    return render_template('developer/console/app/oauth2.html', oauth2_clients=oauth2_clients)


@console_blueprint.route('/console/apps/<string:app_id>/oauth2/create', methods=['POST'])
@app_manager_func
def app_oauth2_create(app_id):
    ApplicationOAuth2Client.create_client(request.app.id)
    return redirect(url_for('console.app_oauth2', app_id=app_id))


@console_blueprint.route('/console/apps/<string:app_id>/oauth2/<string:oauth2_client_id>', methods=['POST'])
@app_manager_func
def app_oauth2_method(app_id, oauth2_client_id):
    client = ApplicationOAuth2Client.objects(id=oauth2_client_id, application_id=request.app.id).get()

    if request.form.get('method') == 'delete':
        client.delete()
    elif request.form.get('method') == 'reset_secret_key':
        client.reset_secret_key()
    elif request.form.get('method') == 'save_redirect_uris':
        client.redirect_uris = [redirect_uri.strip() for redirect_uri in request.form.get('redirect_uris').split('\n')]
        client.save()
    return redirect(url_for('console.app_oauth2', app_id=app_id))


@console_blueprint.route('/console/apps/<string:app_id>/embedded', methods=['GET', 'POST'])
@app_manager_func
def app_embedded(app_id):
    try:
        embedded_info = ApplicationEmbedded.objects(application_id=request.app.id).get()
    except ApplicationEmbedded.DoesNotExist:
        embedded_info = None

    if request.method == 'POST':
        use_embedded = request.form.get('use') is not None
        embedded_iframe_uri = request.form.get('uri')
        campus_ids = request.form.getlist('campus')

        from elasticsearch import Elasticsearch
        es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))

        if not use_embedded and embedded_info:
            es.delete(index='embedded_app_list', doc_type='embedded_app', id=str(embedded_info.id))
            embedded_info.delete()
            embedded_info = None
        elif use_embedded:
            if not embedded_info:
                embedded_info = ApplicationEmbedded()
                embedded_info.application_id = request.app.id

            embedded_info.iframe_uri = embedded_iframe_uri
            embedded_info.campus_ids = campus_ids
            embedded_info.save()
            embedded_info = ApplicationEmbedded.objects(application_id=request.app.id).get()

            es.index(index='embedded_app_list', doc_type='embedded_app', id=str(embedded_info.id), body={
                'app_id': str(request.app.id),
                'name': request.app.name,
                'description': request.app.description,
                'campus_ids': campus_ids
            })

    return render_template('developer/console/app/embedded.html',
                           campuses=Campus.objects(), use_embedded=embedded_info is not None,
                           embedded_iframe_uri=embedded_info.iframe_uri if embedded_info else '',
                           use_campus_ids=embedded_info.campus_ids if embedded_info else [])
