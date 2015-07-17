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

from functools import wraps
from flask import request, abort, jsonify, session, url_for
from opencampus.endpoint.developer.console.common import is_super_user
from opencampus.server import app
from opencampus.common.campus import get_campus
from opencampus.common.models import CampusGateway, Campus, OAuth2AccessToken
from opencampus.endpoint.developer.console.blueprint import console_blueprint
from opencampus.endpoint.api.blueprint import api_blueprint

CAMPUS_SERIVCE_MENUS = []
CAMPUS_SERIVCE_PARNET = []
CAMPUS_MODULE_MENUS = []


def campus_route(module, rule, **options):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            kwargs.pop('subdomain', None)
            request.campus = get_campus()
            if not request.campus:
                return abort(404)
            return f(*args, **kwargs)
        endpoint = options.pop('endpoint', None)
        menu = options.pop('menu', None)
        parent = options.pop('parent', None)
        app.add_url_rule(rule, endpoint, decorated, **options)
        options.pop('subdomain', None)
        app.add_url_rule(rule, endpoint, decorated, subdomain="<string:subdomain>", **options)
        if menu:
            from flask.helpers import _endpoint_from_view_func
            CAMPUS_SERIVCE_MENUS.append({
                'name': menu,
                'endpoint': (endpoint if endpoint else _endpoint_from_view_func(decorated))
            })
            CAMPUS_SERIVCE_PARNET.append({
            })

        if parent:
            CAMPUS_SERIVCE_PARNET.append({
            })

        return decorated
    return decorator


def check_gateway(access_token, campus_id):
    if not access_token or access_token.access_obj_type != 'gateway':
        return None
    try:
        return CampusGateway.objects(id=access_token.access_obj_id,
                                     campus_id=campus_id).get()
    except CampusGateway.DoesNotExist:
        return None


def gateway_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        request.gateway = check_gateway(request.access_token, request.campus.id)
        if not request.gateway:
            return jsonify({'error': {'code': 'gateway_only_method'}}), 403

        return f(*args, **kwargs)
    return decorated


def api_route(module, rule, **options):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            campus_id = kwargs.get('campus_id', None)
            if campus_id:
                try:
                    request.campus = Campus.objects(id=campus_id).get()
                except Campus.DoesNotExist:
                    return abort(404)

            # check access token
            access_token = None
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                access_token = auth_header[7:]
            elif request.args.get('access_token'):
                access_token = request.args.get('access_token')

            request.access_token = None
            if access_token:
                try:
                    request.access_token = OAuth2AccessToken.objects(access_token=access_token).get()
                except OAuth2AccessToken.DoesNotExist:
                    pass

                if not request.access_token:
                    return jsonify({
                        'error': {
                            'code': 'token_not_exist'
                        }
                    }), 403

            result = f(*args, **kwargs)

            callback = request.args.get('callback', None)
            if callback:
                return app.response_class(callback + '(' + result.data.decode('utf8') + ')',
                                          mimetype='application/javascript')

            return result
        endpoint = options.pop('endpoint', None)
        api_blueprint.add_url_rule(rule, endpoint, decorated, **options)
        return decorated
    return decorator


def get_manager_menus():
    return CAMPUS_MODULE_MENUS


def get_campus_service_menus():
    return CAMPUS_SERIVCE_MENUS


def manager_route(module, rule, **options):
    rule = '/console/campuses/<string:campus_id>/modules/%s%s' % (module, rule)

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            campus_id = kwargs.pop('campus_id', None)

            try:
                request.campus = Campus.objects(id=campus_id).get()
            except Campus.DoesNotExist:
                return abort(404)

            if not is_super_user() and session.get_admin_account() not in request.campus.admins:
                return abort(403)

            return f(*args, **kwargs)

        endpoint = options.pop('endpoint', None)
        menu = options.pop('menu', None)
        console_blueprint.add_url_rule(rule, endpoint, decorated, **options)

        if menu:
            from flask.helpers import _endpoint_from_view_func

            get_manager_menus().append({
                'name': menu,
                'endpoint': 'console.%s' % (endpoint if endpoint else _endpoint_from_view_func(decorated))
            })

        return decorated

    return decorator
