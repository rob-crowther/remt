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

"""
reMarkable tablet lines format parser.
"""

import struct
from itertools import chain

from .data import *

flatten = chain.from_iterable


HEADER_START = b'reMarkable lines with selections and layers'
FMT_HEADER_PAGE = '<{}sI'.format(len(HEADER_START))
FMT_PAGE = '<BBH' # TODO might be 'I'
FMT_LAYER = '<I'
FMT_STROKE = '<IIIfI'
FMT_SEGMENT = '<fffff'

SIZE_HEADER_PAGE = struct.calcsize(FMT_HEADER_PAGE)
SIZE_PAGE = struct.calcsize(FMT_PAGE)
SIZE_LAYER = struct.calcsize(FMT_LAYER)
SIZE_STROKE = struct.calcsize(FMT_STROKE)
SIZE_SEGMENT = struct.calcsize(FMT_SEGMENT)


def parse_segment(n_seg, data):
    x, y, pressure, tilt, _ = struct.unpack_from(FMT_SEGMENT, data.read(SIZE_SEGMENT))
    return Segment(n_seg, x, y, pressure,  tilt)

def parse_stroke(n_stroke, data):
    pen, color, _, width, n = struct.unpack(FMT_STROKE, data.read(SIZE_STROKE))
    items = (parse_segment(i, data) for i in range(n))

    yield Stroke(n_stroke, pen, color, width)
    yield from items
    yield StrokeEnd(n_stroke)

def parse_layer(n_layer, data):
    n, = struct.unpack_from(FMT_LAYER, data.read(SIZE_LAYER))

    items = (parse_stroke(i, data) for i in range(n))

    yield Layer(n_layer)
    yield from flatten(items)
    
def parse_page(n_page, data):
    n, _, _ = struct.unpack_from(FMT_PAGE, data.read(SIZE_PAGE))
    items = (parse_layer(i, data) for i in range(n))

    yield Page(n_page)
    yield from flatten(items)

def parse(data):
    header, n = struct.unpack_from(FMT_HEADER_PAGE, data.read(SIZE_HEADER_PAGE))
    assert header == HEADER_START
    items = (parse_page(i, data) for i in range(n))
    yield from flatten(items)

# vim: sw=4:et:ai
