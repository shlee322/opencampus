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

from datetime import datetime
from flask import Blueprint, request, jsonify, redirect, session, render_template, abort
from opencampus.common.models import CampusGateway, OAuth2AccessToken, ApplicationOAuth2Client,\
    OAuth2AccountAccept, Application, OAuth2AuthorizationCode
from opencampus.endpoint.api.oauth2_scope import SCOPE

api_blueprint = Blueprint('api', __name__, subdomain='apis')


@api_blueprint.route('/oauth2/authorize', methods=['GET', 'POST'])
def oauth2_authorize():
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    response_type = request.args.get('response_type')
    scope = [scope.strip() for scope in request.args.get('scope', '').split(',')]

    if not (client_id and redirect_uri and response_type):
        return jsonify({'error': 'invalid_request'}), 400

    try:
        client = ApplicationOAuth2Client.objects(id=client_id).get()
    except ApplicationOAuth2Client.DoesNotExist:
        return jsonify({'error': 'unauthorized_client'}), 400

    check_redirect_uri = False
    for accept_redirect_uri in client.redirect_uris:
        if redirect_uri.startswith(accept_redirect_uri):
            check_redirect_uri = True

    if not check_redirect_uri:
        return 'redirect_uri error', 400

    if not session.get_account():
        if request.method == 'GET':
            return render_template('api/oauth2/login.html')
        else:
            account_id = request.form.get('account_id')
            account_pw = request.form.get('account_pw')

            from opencampus.module.account.models import Account
            try:
                Account.login(account_id, account_pw)
            except:
                return render_template('api/oauth2/login.html')

    check_accept = True
    try:
        accept = OAuth2AccountAccept.objects(client_id=client_id, account_id=session.get_account().id).get()
        for s in scope:
            if accept and s not in accept.scope:
                check_accept = False

    except OAuth2AccountAccept.DoesNotExist:
        check_accept = False
        accept = None

    if not check_accept:
        if request.method == 'GET':
            return render_template('api/oauth2/permission.html',
                                   app=Application.objects(id=client.application_id).get(),
                                   scope=scope,
                                   scope_name=SCOPE)
        elif request.method == 'POST':
            token = session.get('csrf_token')
            if not token or token != request.form.get('csrf_token'):
                return abort(403)

            if not accept:
                accept = OAuth2AccountAccept()
                accept.client_id = client_id
                accept.account_id = session.get_account().id
                accept.created_at = datetime.utcnow()

            accept.scope = scope
            accept.save()

    if response_type == 'token':
        token = OAuth2AccessToken.create_token('account', session.get_account().id, client_id=client.id, scope=accept.scope)
        token.save()
        return redirect(redirect_uri + '?access_token=' + token.access_token)
    elif response_type == 'code':
        code = OAuth2AuthorizationCode.create_code(client.id, session.get_account().id, scope=accept.scope)
        return redirect(redirect_uri + '?code=' + code.code)
    else:
        return jsonify({'error': 'unsupported_response_type'}), 400


@api_blueprint.route('/oauth2/token', methods=['POST'])
def oauth2_token():
    grant_type = request.form.get('grant_type')

    if grant_type == 'authorization_code':
        """
        일반 사용자가 앱에서 토큰을 획득할 때 사용
        """
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        redirect_uri = request.form.get('redirect_uri')     # TODO
        code = request.form.get('code')

        try:
            code = OAuth2AuthorizationCode.objects(code=code, client_id=client_id).get()
        except OAuth2AuthorizationCode.DoesNotExist:
            return jsonify({'error': 'invalid_request'}), 400

        try:
            client = ApplicationOAuth2Client.objects(id=code.client_id).get()
        except ApplicationOAuth2Client.DoesNotExist:
            return jsonify({'error': 'unauthorized_client'}), 400

        if client_secret != client.secret_key:
            return jsonify({'error': 'unauthorized_client'}), 400

        token = OAuth2AccessToken.create_token('account', code.account_id, scope=code.scope)
        token.client_id = client.id
        token.save()
        code.delete()

        expires_in = token.expires_at - datetime.utcnow()
        expires_in = expires_in.days * 86400 + expires_in.seconds
        return jsonify({
            'access_token': token.access_token,
            'expires_in': expires_in,
            'token_type': 'Bearer',
            'refresh_token': token.refresh_token
        })

    elif grant_type == 'client_credentials':
        """
        게이트웨이에서 토큰 획득 용으로 사용
        """
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        try:
            gateway = CampusGateway.objects(id=client_id, secret_key=client_secret).get()
            token = OAuth2AccessToken.create_token('gateway', gateway.id)
            expires_in = token.expires_at - datetime.utcnow()
            expires_in = expires_in.days * 86400 + expires_in.seconds
            return jsonify({
                'access_token': token.access_token,
                'expires_in': expires_in,
                'token_type': 'Bearer',
                'refresh_token': token.refresh_token
            })
        except CampusGateway.DoesNotExist:
            pass
        return jsonify({'error': 'invalid_request'}), 400
    elif grant_type == 'refresh_token':
        return jsonify({'error': 'unsupported_response_type'}), 400
    else:
        return jsonify({'error': 'unsupported_grant_type'}), 400
