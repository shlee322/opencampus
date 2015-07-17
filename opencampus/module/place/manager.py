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

from flask import render_template, request, redirect, url_for
from opencampus.common import modulemanager
from opencampus.module.place.models import Place


@modulemanager.manager_route('place', '/manager', menu='장소 관리', methods=['GET','POST'])
def place_manager():
    if request.method == 'POST':
        new_place = None
        try:
            names = [name.strip() for name in request.form.get('new_place_names').split(',')]
            latitude = float(request.form.get('new_place_latitude'))
            longitude = float(request.form.get('new_place_longitude'))

            place = Place(
                campus_id=request.campus.id,
                names=names,
                location=[latitude, longitude]
            )
            place.save()
            new_place = place
        except ValueError:
            pass

        for place in Place.objects(campus_id=request.campus.id):
            if new_place and new_place.id == place.id:
                continue
            place.names = [name.strip() for name in request.form.get('%s_names' % place.id).split(',')]
            latitude = float(request.form.get('%s_latitude' % place.id))
            longitude = float(request.form.get('%s_longitude' % place.id))
            place.location = [latitude, longitude]
            place.save()

    places = Place.objects(campus_id=request.campus.id)
    return render_template('module/place/manager/place_manager.html', places=places,
                           module_menus=modulemanager.get_manager_menus())


@modulemanager.manager_route('place', '/manager/delete', methods=['POST'])
def place_manager_place_delete():
    place = Place.objects(id=request.form.get('place_id'), campus_id=request.campus.id)
    place.delete()
    return redirect(url_for('console.place_manager', campus_id=request.campus.id))
