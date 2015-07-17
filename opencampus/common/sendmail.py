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

import boto.ses
from opencampus.server import app


def send_email(subject, body, to_addresses):
    conn = boto.ses.connect_to_region(
        'us-west-2',
        aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
    return conn.send_email('support@opencampus.kr', subject, body, to_addresses)
