# Copyright (C) 2015 opencampus.kr
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, ordfsdfasf
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import hashlib
from Crypto import Random
from flask import request
from mongoengine import Document, fields
from datetime import datetime, timedelta
from opencampus.server import app
from opencampus.gateway.gateway import Gateway as GatewayObject


class Session(Document):
    session_id = fields.StringField(primary_key=True)
    session_secret = fields.StringField()
    created_at = fields.DateTimeField()
    expires_at = fields.DateTimeField()
    account_list = fields.ListField(fields.ObjectIdField())
    admin_account_list = fields.ListField(fields.StringField())
    ip_address = fields.StringField()
    data = fields.StringField()

    @staticmethod
    def create_session():
        r = Random.new()
        session = Session()
        now = datetime.utcnow()
        sha512 = hashlib.sha512()
        sha512.update(r.read(64))
        sha512.update(datetime.now().isoformat().encode())
        sha512.update(request.remote_addr.encode('utf-8'))
        session.session_id = sha512.hexdigest()
        session.session_secret = str(binascii.hexlify(r.read(64)), 'utf-8')
        session.created_at = now
        session.expires_at = now + timedelta(days=30)
        session.ip_address = request.remote_addr
        return session

    def is_expired(self):
        return self.expires_at < datetime.utcnow()


class Campus(Document):
    univ_name = fields.StringField()
    univ_type = fields.StringField(default='대학교')
    campus_name = fields.StringField()
    created_at = fields.DateTimeField()
    domain = fields.StringField(unique=True)
    gateway_apis = fields.StringField()
    menus = fields.StringField(default='[]')
    admins = fields.ListField(fields.StringField())

    def __init__(self, *args, **kwargs):
        Document.__init__(self, *args, **kwargs)
        self._gateway = None

    @staticmethod
    def create_campus(univ_name, univ_type, campus_name, admins=None):
        if not admins:
            admins = []
        campus = Campus()
        campus.univ_name = univ_name
        campus.univ_type = univ_type
        campus.campus_name = campus_name
        campus.created_at = datetime.utcnow()
        campus.admins = admins
        campus.save()
        return campus

    def save(self, *args, **kwargs):
        Document.save(self, *args, **kwargs)
        from elasticsearch import Elasticsearch
        es = Elasticsearch(hosts=app.config.get('ELASTICSEARCH_HOSTS'))
        es.index(index='campus_list', doc_type='campus', id=str(self.id), body={
            'univ_name': '%s%s' % (self.univ_name, self.univ_type),
            'campus_name': self.campus_name
        })

    def get_gateway(self):
        if not self._gateway:
            self._gateway = GatewayObject(self)
        return self._gateway

    def get_menus(self):
        import json
        return json.loads(self.menus)


class CampusGateway(Document):
    campus_id = fields.ObjectIdField()
    secret_key = fields.StringField()
    created_at = fields.DateTimeField()

    @staticmethod
    def create_gateway(campus_id):
        gateway = CampusGateway()
        gateway.campus_id = campus_id
        gateway.reset_secret_key(False)
        gateway.created_at = datetime.utcnow()
        gateway.save()
        return gateway

    def reset_secret_key(self, save=True):
        r = Random.new()
        self.secret_key = str(binascii.hexlify(r.read(32)), 'utf-8')

        if save:
            self.save()


class Application(Document):
    name = fields.StringField()
    created_at = fields.DateTimeField()
    description = fields.StringField(default='')
    admins = fields.ListField(fields.StringField())


class ApplicationEmbedded(Document):
    application_id = fields.ObjectIdField()
    iframe_uri = fields.StringField(default='')
    campus_ids = fields.ListField(fields.ObjectIdField())

    meta = {
        'indexes': [
            {
                'fields': ['application_id'],
                'unique': True
            }
        ],
    }


class ApplicationOAuth2Client(Document):
    application_id = fields.ObjectIdField()
    secret_key = fields.StringField()
    created_at = fields.DateTimeField()
    redirect_uris = fields.ListField(fields.StringField())
    meta = {'collection': 'application_oauth2_client'}

    @staticmethod
    def create_client(application_id):
        client = ApplicationOAuth2Client()
        client.application_id = application_id
        client.reset_secret_key(False)
        client.created_at = datetime.utcnow()
        client.save()
        return client

    def reset_secret_key(self, save=True):
        r = Random.new()
        self.secret_key = str(binascii.hexlify(r.read(32)), 'utf-8')

        if save:
            self.save()


class OAuth2AccessToken(Document):
    access_token = fields.StringField(primary_key=True)
    refresh_token = fields.StringField(unique=True)
    expires_at = fields.DateTimeField()
    access_obj_type = fields.StringField()
    access_obj_id = fields.ObjectIdField()
    scope = fields.ListField(fields.StringField())
    client_id = fields.ObjectIdField()
    meta = {'collection': 'oauth2_access_token'}

    @staticmethod
    def create_token(access_obj_type, access_obj_id, expires=60 * 60 * 24, client_id=None, scope=None):
        if not scope:
            scope = []
        r = Random.new()
        token = OAuth2AccessToken()
        token.access_token = str(binascii.hexlify(r.read(32)), 'utf-8')
        token.refresh_token = str(binascii.hexlify(r.read(32)), 'utf-8')
        token.expires_at = datetime.utcnow() + timedelta(days=expires / 86400, seconds=expires % 86400)
        token.access_obj_type = access_obj_type
        token.access_obj_id = access_obj_id
        token.client_id = client_id
        token.scope = scope
        token.save()
        return token


class OAuth2AuthorizationCode(Document):
    code = fields.StringField(primary_key=True)
    client_id = fields.ObjectIdField()
    account_id = fields.ObjectIdField()
    created_at = fields.DateTimeField()
    scope = fields.ListField(fields.StringField())
    meta = {'collection': 'oauth2_authorization_code'}

    @staticmethod
    def create_code(client_id, account_id, scope=None):
        if not scope:
            scope = []
        r = Random.new()
        code = OAuth2AuthorizationCode()
        code.code = str(binascii.hexlify(r.read(32)), 'utf-8')
        code.client_id = client_id
        code.account_id = account_id
        code.created_at = datetime.utcnow()
        code.scope = scope
        code.save()
        return code


class OAuth2AccountAccept(Document):
    client_id = fields.ObjectIdField()
    account_id = fields.ObjectIdField()
    created_at = fields.DateTimeField()
    scope = fields.ListField(fields.StringField())
    meta = {
        'collection': 'oauth2_account_accept',
        'indexes': [
            {
                'fields': ['client_id', 'account_id'],
                'unique': True
            }
        ]
    }
