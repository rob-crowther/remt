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
reMarkable strokes drawing using Cairo library.
"""

import cairo
from collections import namedtuple
from contextlib import contextmanager
from functools import singledispatch

from .data import *


WIDTH = 1404
HEIGHT = 1872

STROKE_COLOR = {
    0: (0, 0, 0),
    1: (128, 128, 128),
    2: (255, 255, 255),
}

STROKE_PEN = {
    0: lambda v: v,
    1: lambda v: v,
    # Pen / Fineliner
    2: lambda v: v._replace(width=32 * v.width ** 2 - 116 * v.width + 107),
    4: lambda v: v._replace(width=32 * v.width ** 2 - 116 * v.width + 107),
    # Marker
    3: lambda v: v._replace(width=64 * v.width - 112, opacity=0.9),
    # Highlighter
    5: lambda v: v._replace(width=30, opacity=0.2),
    # Eraser
    6: lambda v: v._replace(width=1280 * v.width ** 2 - 4800 * v.width + 4510, color=2),
    # Pencil-Sharp
    7: lambda v: v._replace(width=16 * v.width - 27, opacity=0.9),
    # Erase area
    8: lambda v: v._replace(opacity=0),
}

StrokePen = namedtuple('StrokePen', ['width', 'color', 'opacity'])


@singledispatch
def draw(item, context):
    raise NotImplementedError('Unknown item to draw: {}'.format(item))

@draw.register(Page)
def _(page, context):
    pass

@draw.register(Layer)
def _(layer, context):
    pass

@draw.register(Stroke)
def _(stroke, context):
    context.new_path()

    pen = StrokePen(stroke.width, stroke.color, 1)
    pen = STROKE_PEN[stroke.pen](pen)
    color = STROKE_COLOR[pen.color] + (pen.opacity,)

    context.set_source_rgba(*color)
    context.set_line_width(pen.width)

@draw.register(StrokeEnd)
def _(segment_end, context):
    context.stroke()

@draw.register(Segment)
def _(segment, context):
    context.line_to(segment.x, segment.y)

@contextmanager
def draw_context(fn):
    surface = cairo.PDFSurface(fn, WIDTH, HEIGHT)
    try:
        context = cairo.Context(surface)
        yield context
    finally:
        surface.finish()


# vim: sw=4:et:ai
