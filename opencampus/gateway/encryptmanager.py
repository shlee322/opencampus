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
import base64
import json
from urllib import parse
from datetime import datetime
from Crypto import Random
from Crypto.Cipher import AES


class EncryptManager:
    def __init__(self, secret_key=None):
        self.secret_key = None
        if secret_key:
            self.set_key(secret_key)

    def set_key(self, secret_key):
        self.secret_key = binascii.unhexlify(secret_key)

    def encrypt(self, data):
        data = json.dumps(data)
        time = datetime.utcnow().isoformat()

        encrypted_body = parse.urlencode({
            'data': base64.b64encode(data.encode('utf-8')),
            'time': base64.b64encode(time.encode('utf-8'))
        })

        encrypted_body += (AES.block_size - len(encrypted_body) % AES.block_size) * chr(0)

        iv = Random.new().read(AES.block_size)
        aes_cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        body = parse.urlencode({
            'cipher': 'aes-256-cbc',
            'iv': base64.b64encode(iv),
            'encrypted_body': base64.b64encode(aes_cipher.encrypt(encrypted_body))
        })

        return body

    def decrypt(self, body):
        if type(body) is str:
            body = dict(parse.parse_qsl(body))

        encrypted_body = body.get('encrypted_body', None)
        iv = body.get('iv', None)

        if not encrypted_body or not iv:
            raise ValueError()

        encrypted_body = base64.b64decode(encrypted_body)
        iv = base64.b64decode(iv)

        aes_cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
        body = parse.parse_qs(aes_cipher.decrypt(encrypted_body))
        body = {key.decode('utf8'): value[0].decode('utf8') for (key, value) in body.items()}

        data = base64.b64decode(body['data']).decode('utf-8')
        time = base64.b64decode(body['time']).decode('utf-8')

        # TODO : time check
        return json.loads(data)
