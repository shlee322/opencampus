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
from flask.sessions import SessionInterface, SessionMixin
from opencampus.common.models import Session
from opencampus.common.db import db
from opencampus.server import app


class OpenCampusSession(SessionMixin):
    def __init__(self, db_session=None):
        self.modified = False
        self.db_session = db_session
        self.data = {}

        if not db_session:
            self.db_session = Session.create_session()
        elif self.db_session.data:
            self.data = json.loads(self.db_session.data)

    def __getitem__(self, *args, **kwargs):
        return self.data.__getitem__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self.data.__contains__(*args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        self.modified = True
        return self.data.__setitem__(*args, **kwargs)

    def __delitem__(self, *args, **kwargs):
        self.modified = True
        return self.data.__delitem__(*args, **kwargs)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def get_session_id(self):
        return self.db_session.session_id

    def get_session_secret(self):
        return self.db_session.session_secret

    def get_session_expires_at(self):
        return self.db_session.expires_at

    def get_account(self):
        if len(self.db_session.account_list) < 1:
            return None

        account_oid = self.db_session.account_list[0]
        from opencampus.module.account.models import Account
        try:
            return Account.objects(id=account_oid).get()
        except Account.DoesNotExist:
            self.db_session.account_list = []
            self.modified = True
            return None

    def get_admin_account(self):
        if len(self.db_session.admin_account_list) < 1:
            return None

        return self.db_session.admin_account_list[0]

    def add_account(self, account):
        # TODO : M-Account
        self.db_session.account_list = [account.id]
        self.modified = True

    def del_account(self, account):
        # TODO : M-Account
        self.db_session.account_list = []
        self.modified = True

    def set_admin_account(self, email):
        self.db_session.admin_account_list = [email]
        self.modified = True

    def del_admin_account(self):
        self.db_session.admin_account_list = []
        self.modified = True

    def save(self):
        self.db_session.data = json.dumps(self.data) if self.data else None
        self.db_session.save()


class OpenCampusSessionInterface(SessionInterface):
    def __init__(self, db):
        self.db = db

    def open_session(self, app, request):
        session_id = request.cookies.get('session_id')
        session_secret = request.cookies.get('session_secret')

        if session_id:
            try:
                session = Session.objects.get(session_id=session_id)
            except Session.DoesNotExist:
                return OpenCampusSession()

            if session.session_secret != session_secret:
                app.logger.warning('session attack!')
                session.delete()
                return OpenCampusSession()

            if session.is_expired():
                session.delete()
                return OpenCampusSession()

            # TODO : 자동연장

            return OpenCampusSession(session)

        return OpenCampusSession()

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)

        if not session:
            response.delete_cookie('session_id', domain=domain)
            response.delete_cookie('session_secret', domain=domain)
            return

        session.save()
        response.set_cookie('session_id', session.get_session_id(),
                            expires=session.get_session_expires_at(),
                            httponly=True, domain=domain, secure=not app.debug)
        response.set_cookie('session_secret', session.get_session_secret(),
                            expires=session.get_session_expires_at(),
                            httponly=True, domain=domain, secure=not app.debug)


app.session_interface = OpenCampusSessionInterface(db)