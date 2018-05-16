#
# remt - reMarkable tablet command-line tools
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

"""
reMarkable tablet lines format parser.
"""

import math
import struct
from collections import namedtuple
from itertools import chain

from .data import *

flatten = chain.from_iterable


HEADER_START = b'reMarkable lines with selections and layers'
FMT_HEADER_PAGE = struct.Struct('<{}sI'.format(len(HEADER_START)))
FMT_PAGE = struct.Struct('<BBH') # TODO might be 'I'
FMT_LAYER = struct.Struct('<I')
FMT_STROKE = struct.Struct('<IIIfI')
FMT_SEGMENT = struct.Struct('<fffff')


def parse_item(fmt, fin):
    """
    Read number of bytes from a file and parse the data of a drawing item
    using a format.

    :param fmt: Struct format object.
    :param fin: File object.
    """
    buff = fin.read(fmt.size)
    return fmt.unpack(buff)

def parse_segment(n_seg, data):
    x, y, pressure, tilt_x, tilt_y = parse_item(FMT_SEGMENT, data)
    return Segment(n_seg, x, y, pressure, tilt_x, tilt_y)

def parse_stroke(n_stroke, data):
    pen, color, _, width, n = parse_item(FMT_STROKE, data)

    segments = [parse_segment(i, data) for i in range(n)]
    stroke = Stroke(n_stroke, pen, color, width, segments)

    yield stroke

def parse_layer(n_layer, data):
    n, = parse_item(FMT_LAYER, data)

    items = (parse_stroke(i, data) for i in range(n))

    yield Layer(n_layer)
    yield from flatten(items)
    
def parse_page(n_page, data):
    n, _, _ = parse_item(FMT_PAGE, data)
    items = (parse_layer(i, data) for i in range(n))

    yield Page(n_page)
    yield from flatten(items)
    yield PageEnd(n_page)

def parse(data):
    header, n = parse_item(FMT_HEADER_PAGE, data)
    assert header == HEADER_START

    items = (parse_page(i, data) for i in range(n))
    yield from flatten(items)

# vim: sw=4:et:ai
