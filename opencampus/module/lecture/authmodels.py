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

import binascii
from datetime import datetime
from Crypto import Random
from mongoengine import Document, EmbeddedDocument, fields


class LectureAuthRequestInfo(Document):
    lecture_id = fields.ObjectIdField()
    auth_type = fields.StringField()
    auth_code = fields.StringField()
    created_at = fields.DateTimeField()
    account_id = fields.ObjectIdField()

    @staticmethod
    def create_request(lecture_id, auth_type, account_id):
        r = Random.new()
        
        request_info = LectureAuthRequestInfo()
        request_info.lecture_id = lecture_id
        request_info.auth_type = auth_type
        request_info.created_at = datetime.utcnow()
        request_info.account_id = account_id

        if auth_type == 'email':
            request_info.auth_code = str(binascii.hexlify(r.read(32)), 'utf-8')
        else:
            request_info.auth_code = ''
            for i in range(4):
                from Crypto.Random import random
                request_info.auth_code += random.choice(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

        request_info.save()
        return request_info.auth_code
