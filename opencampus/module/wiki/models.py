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

from mongoengine import Document, fields

class WikiPage(Document):
    campus_id = fields.ObjectIdField()
    name = fields.StringField()
    created_at = fields.DateTimeField()
    updated_at = fields.DateTimeField()
    content = fields.StringField()

class WikiPageFile(Document):
    campus_id = fields.ObjectIdField()
    wiki_page = fields.ReferenceField()
    created_at = fields.DateTimeField()
    ip_address = fields.StringField()
    account = fields.ReferenceField()
    file = fields.FileField()

class WikiPageHistory(Document):
    campus_id = fields.ObjectIdField()
    wiki_page = fields.ReferenceField()
    created_at = fields.DateTimeField()
    ip_address = fields.StringField()
    account = fields.ReferenceField()
    patch = fields.StringField()

