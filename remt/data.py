#
# remt - reMarkable tablet tools
#
# Copyright (C) 2018 by Artur Wroblewski <wrobell@riseup.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from collections import namedtuple

Page = namedtuple('Page', ['number'])
Layer = namedtuple('Layer', ['number'])
Stroke = namedtuple(
    'Stroke',
    ['number', 'pen', 'color', 'width', 'pressure', 'tilt', 'style']
)
StrokeEnd = namedtuple('StrokeEnd', ['number'])
Segment = namedtuple('Segment', ['number', 'x', 'y'])

Style = namedtuple('Style', ['width', 'color', 'join', 'cap'])
Color = namedtuple('Color', ['red', 'green', 'blue', 'alpha'])

# vim: sw=4:et:ai