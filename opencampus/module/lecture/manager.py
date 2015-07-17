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

from flask import render_template, request, redirect, url_for
from opencampus.common import modulemanager
from opencampus.module.lecture.searchengine import init_index


@modulemanager.manager_route('lecture', '/manager', menu='강의 관리')
def lecture_manager():
    return render_template('module/lecture/manager/lecture_manager.html',
                           module_menus=modulemanager.get_manager_menus())


@modulemanager.manager_route('lecture', '/init_recture_index', methods=['POST'])
def init_recture_index():
    init_index(str(request.campus.id))
    return redirect(url_for('console.lecture_manager', campus_id=request.campus.id))
