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

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from flask import Response
from opencampus.server import app


def get_bucket():
    conn = S3Connection(
        aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
    bucket = conn.get_bucket(app.config.get('AWS_S3_BUCKET'))
    return bucket


def get(path):
    bucket = get_bucket()
    try:
        obj = bucket.get_key(path)
        obj.open_read()
        headers = dict(obj.resp.getheaders())
        return Response(obj, headers=headers)
    except S3ResponseError as e:
        return Response('error', status=e.status)


def put(path, obj):
    bucket = get_bucket()
    sml = bucket.new_key(path)
    sml.set_metadata('Content-Type', obj.content_type)
    sml.set_contents_from_file(obj)
