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

import bcrypt
from mongoengine import Document, EmbeddedDocument, fields
from opencampus.module.account.errors import AccountNotFound, DoesNotMatchPassword


class Account(Document):
    campus_id = fields.ObjectIdField()
    account_id = fields.StringField(unique=True)
    account_pw = fields.StringField()
    nickname = fields.StringField()
    created_at = fields.DateTimeField()
    account_type = fields.StringField()
    student_id = fields.StringField()
    auth_info = fields.StringField()
    name = fields.StringField()
    departments = fields.ListField(fields.StringField())

    meta = {
        'indexes': [
            {
                'fields': ['campus_id', 'student_id'],
                'unique': True
            },
        ],
    }

    @staticmethod
    def create_account(campus_id, account_id, account_pw, nickname, account_type, student_id):
        account = Account(
            campus_id=campus_id,
            account_id=account_id,
            account_pw=bcrypt.hashpw(account_pw.encode('utf-8'), bcrypt.gensalt()),
            nickname=nickname,
            account_type=account_type,
            student_id=student_id
        )
        account.save()
        return account

    @staticmethod
    def valid_account_id(account_id):
        import re
        return re.search(r'^[a-z]', account_id) and re.search(r'^[a-z0-9_-]{6,30}$', account_id)

    @staticmethod
    def valid_account_pw(account_pw):
        import re
        count = 0

        if re.search(r'[a-z]', account_pw):
            count += 1

        if re.search(r'[A-Z]', account_pw):
            count += 1

        if re.search(r'[0-9]', account_pw):
            count += 1

        if re.search(r"[~!@#$%\^&*()_+`\-={}|[\]\\:\";'<>?,./]", account_pw):
            count += 1

        return not (count < 2 or (count == 2 and len(account_pw) < 10) or len(account_pw) < 8)

    @staticmethod
    def valid_nickname(nickname):
        return 3 <= len(nickname) <= 10

    @staticmethod
    def login(account_id, account_pw):
        try:
            account = Account.objects(account_id=account_id).get()
        except Account.DoesNotExist:
            raise AccountNotFound()

        if bcrypt.hashpw(account_pw.encode('utf-8'), account.account_pw.encode('utf-8')) != account.account_pw.encode('utf-8'):
            raise DoesNotMatchPassword()

        from flask import session
        session.add_account(account)

        return account