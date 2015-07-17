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
# You should have recei ved a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import request, render_template, abort, jsonify, redirect, url_for, session
from opencampus.common import modulemanager

@modulemanager.campus_route('wiki', '/wiki/')
def wiki_main():
    return render_template('module/wiki/main.html')

@modulemanager.campus_route('wiki', '/wiki/<int:article_id>')
def wiki_content(article_id):
    return render_template('module/wiki/content.html')

@modulemanager.campus_route('wiki', '/wiki/<int:article_id>/edit')
def wiki_edit(article_id):
    return render_template('module/wiki/edit.html')

@modulemanager.campus_route('wiki', '/wiki/<int:article_id>/history')
def wiki_history(article_id):
    return render_template('module/wiki/history.html')

