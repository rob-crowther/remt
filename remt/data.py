#
# remt - reMarkable tablet command-line tools
#
# Copyright (C) 2018-2019 by Artur Wroblewski <wrobell@riseup.net>
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
PageEnd = namedtuple('PageEnd', ['number'])

Layer = namedtuple('Layer', ['number'])
Stroke = namedtuple(
    'Stroke',
    ['number', 'pen', 'color', 'width', 'segments']
)
Segment = namedtuple(
    'Segment',
    ['number', 'x', 'y', 'speed', 'direction', 'width', 'pressure'],
)

Style = namedtuple(
    'Style',
    ['color', 'join', 'cap', 'brush', 'tool_line']
)
Color = namedtuple('Color', ['red', 'green', 'blue', 'alpha'])
Context = namedtuple('Context', ['cr_surface', 'cr_ctx', 'pdf_doc', 'page_number'])

# vim: sw=4:et:ai
