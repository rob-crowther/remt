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

import math
import struct
from collections import namedtuple
from itertools import chain
from functools import partial
from cytoolz.functoolz import pipe
from cytoolz.itertoolz import sliding_window
from cytoolz.curried import map

from .data import *

flatten = chain.from_iterable


HEADER_START = b'reMarkable lines with selections and layers'
FMT_HEADER_PAGE = struct.Struct('<{}sI'.format(len(HEADER_START)))
FMT_PAGE = struct.Struct('<BBH') # TODO might be 'I'
FMT_LAYER = struct.Struct('<I')
FMT_STROKE = struct.Struct('<IIIfI')
FMT_SEGMENT = struct.Struct('<fffff')


RStroke = namedtuple('RStroke', ['number', 'pen', 'color', 'width'])
RSegment = namedtuple(
    'RSegment',
    ['stroke', 'number', 'x', 'y', 'pressure', 'tilt']
)


def parse_bytes(fmt, fin):
    """
    Read number of bytes from a file and parse the data with a struct
    format.

    :param fmt: Struct format object.
    :param fin: File object.
    """
    buff = fin.read(fmt.size)
    return fmt.unpack(buff)

def parse_segment(stroke, n_seg, data):
    x, y, pressure, tilt, _ = parse_bytes(FMT_SEGMENT, data)
    return RSegment(stroke, n_seg, x, y, pressure, tilt)

def parse_stroke(n_stroke, data):
    pen, color, _, width, n = parse_bytes(FMT_STROKE, data)

    stroke = RStroke(n_stroke, pen, color, width)
    items = (parse_segment(stroke, i, data) for i in range(n))

    yield stroke
    yield from items
    yield StrokeEnd(n_stroke)

def parse_layer(n_layer, data):
    n, = parse_bytes(FMT_LAYER, data)

    items = (parse_stroke(i, data) for i in range(n))

    yield Layer(n_layer)
    yield from flatten(items)
    
def parse_page(n_page, data):
    n, _, _ = parse_bytes(FMT_PAGE, data)
    items = (parse_layer(i, data) for i in range(n))

    yield Page(n_page)
    yield from flatten(items)

def inject_into(cond, func, items):
    """
    Inject new items into stream of items.

    The `cond` and `func` functions accept two parameters - current and
    next item.

    :param cond: Function to check if new items should be injected.
    :param func: Function to generate new items.
    :param items: Stream of items.
    """
    for v1, v2 in sliding_window(2, items):
        if cond(v1, v2):
            yield from func(v1, v2)
        else:
            yield v1
    yield v2

def is_new_stroke(s1, s2):
    return isinstance(s1, RSegment) and isinstance(s2, RSegment) \
        and s1.stroke.pen in (0, 1) \
        and not (
            math.isclose(s1.pressure, s2.pressure)
            and math.isclose(s1.tilt, s2.tilt)
        )

def new_stroke(s1, s2):
    s = s1.stroke
    stroke = RStroke(None, s.pen, s.color, s.width)
    yield s1
    yield s2
    yield StrokeEnd(None)
    yield stroke

def is_stroke_change(s1, s2):
    return isinstance(s1, RStroke) and isinstance(s2, RSegment)

def to_stroke(s1, s2):
    yield Stroke(
        s1.number, s1.pen, s1.color, s1.width, s2.pressure, s2.tilt, None
    )

def is_seg(segment):
    return isinstance(segment, RSegment)

def to_seg(segment):
    return Segment(segment.number, segment.x, segment.y) \
        if is_seg(segment) else segment

def parse(data):
    header, n = parse_bytes(FMT_HEADER_PAGE, data)
    assert header == HEADER_START

    # split existing strokes if necessary
    reset_stroke = partial(inject_into, is_new_stroke, new_stroke)
    convert_stroke = partial(inject_into, is_stroke_change, to_stroke)
    convert_seg = map(to_seg)

    items = (parse_page(i, data) for i in range(n))
    items = pipe(items, flatten, reset_stroke, convert_stroke, convert_seg)
    yield from items

# vim: sw=4:et:ai
