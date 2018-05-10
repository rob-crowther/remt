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
    0: Color(0, 0, 0, 1),
    1: Color(0.5, 0.5, 0.5, 1),
    2: Color(1, 1, 1, 1),
}

STYLE = {
    0: lambda st: Style(
        (5 * st.tilt) * (6 * st.width - 10) * (1 + 2 * st.pressure ** 3),
        STROKE_COLOR[st.color],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    1: lambda st: Style(
        (10 * st.tilt - 2) * (8 * st.width - 14),
        STROKE_COLOR[st.color]._replace(alpha=(st.pressure - 0.2) ** 2),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Pen / Fineliner
    2: lambda st: Style(
        32 * st.width ** 2 - 116 * st.width + 107,
        STROKE_COLOR[st.color],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    4: lambda st: Style(
        32 * st.width ** 2 - 116 * st.width + 107,
        STROKE_COLOR[st.color],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Marker
    3: lambda st: Style(
        64 * st.width - 112,
        STROKE_COLOR[st.color]._replace(alpha=0.9),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Highlighter
    5: lambda st: Style(
        30,
        STROKE_COLOR[st.color]._replace(alpha=0.2),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_SQUARE,
    ),
    # Eraser
    6: lambda st: Style(
        1280 * st.width ** 2 - 4800 * st.width + 4510,
        STROKE_COLOR[2],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Pencil-Sharp
    7: lambda st: Style(
        16 * st.width - 27,
        STROKE_COLOR[st.color]._replace(alpha=0.9),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Erase area
    8: lambda st: Style(
        st.width,
        STROKE_COLOR[st.color]._replace(alpha=0),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
}


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

    style = stroke.style
    context.set_line_width(style.width)
    context.set_source_rgba(*style.color)
    context.set_line_join(style.join)
    context.set_line_cap(style.cap)

    # round line join is important with thicker lines
    #context.set_line_join(cairo.LINE_JOIN_ROUND)
    # TODO: not for highlighter
    #context.set_line_cap(cairo.LINE_CAP_ROUND)

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


@singledispatch
def reset_style(item):
    return item

@reset_style.register(Stroke)
def _(stroke):
    color = STROKE_COLOR[stroke.color]
    style = STYLE[stroke.pen](stroke)
    return stroke._replace(style=style)

# vim: sw=4:et:ai
