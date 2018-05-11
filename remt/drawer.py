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
import logging
from collections import namedtuple
from contextlib import contextmanager
from functools import singledispatch

from .data import *


logger = logging.getLogger(__name__)


WIDTH = 1404
HEIGHT = 1872

COLOR_STROKE = {
    0: Color(0, 0, 0, 1),
    1: Color(0.5, 0.5, 0.5, 1),
    2: Color(1, 1, 1, 1),
}

COLOR_HIGHLIGHTER = Color(1.0, 0.8039, 0.0, 0.1)

STYLE_DEFAULT = Style(
    1,
    COLOR_STROKE[0],
    cairo.LINE_JOIN_ROUND,
    cairo.LINE_CAP_ROUND,
)

STYLE_HIGHLIGHTER = Style(
    30,
    COLOR_HIGHLIGHTER,
    cairo.LINE_JOIN_ROUND,
    cairo.LINE_CAP_SQUARE,
)


STYLE = {
#0: lambda st: Style(
#    (5 * st.tilt) * (6 * st.width - 10) * (1 + 2 * st.pressure ** 3),
#    COLOR_STROKE[st.color],
#    cairo.LINE_JOIN_ROUND,
#    cairo.LINE_CAP_ROUND,
#),
#1: lambda st: Style(
#    (10 * st.tilt - 2) * (8 * st.width - 14),
#    COLOR_STROKE[st.color]._replace(alpha=(st.pressure - 0.2) ** 2),
#    cairo.LINE_JOIN_ROUND,
#    cairo.LINE_CAP_ROUND,
#),
    # Pen
#   2: lambda st: Style(
#       32 * st.width ** 2 - 116 * st.width + 107,
#       COLOR_STROKE[st.color],
#       cairo.LINE_JOIN_ROUND,
#       cairo.LINE_CAP_ROUND,
#   ),
    # Fineliner
    4: lambda st: Style(
        32 * st.width ** 2 - 116 * st.width + 107,
        COLOR_STROKE[st.color],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
#   # Marker
#   3: lambda st: Style(
#       64 * st.width - 112,
#       COLOR_STROKE[st.color]._replace(alpha=0.9),
#       cairo.LINE_JOIN_ROUND,
#       cairo.LINE_CAP_ROUND,
#   ),
    # Highlighter
    5: lambda st: STYLE_HIGHLIGHTER,
    # Eraser
    6: lambda st: Style(
        1280 * st.width ** 2 - 4800 * st.width + 4510,
        COLOR_STROKE[2],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Pencil - Sharp
    7: lambda st: Style(
        16 * st.width - 27,
        COLOR_STROKE[st.color],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
    # Erase area
    8: lambda st: Style(
        st.width,
        COLOR_STROKE[st.color]._replace(alpha=0),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
    ),
}


@singledispatch
def draw(item, context):
    raise NotImplementedError('Unknown item to draw: {}'.format(item))

@draw.register(Page)
def _(page, context):
    if page.number:
        context.show_page()

@draw.register(Layer)
def _(layer, context):
    pass

@draw.register(Stroke)
def _(stroke, context):
    color = COLOR_STROKE[stroke.color]
    f = STYLE.get(stroke.pen)
    if f is not None:
        style = f(stroke)
    else:
        logger.debug('Not supported pen for stroke: {}'.format(stroke))
        #style = STYLE_DEFAULT

        return
    # on new path, the position of point is undefined and first `line_to`
    # call acts as `move_to`
    context.new_path()

    context.set_line_width(style.width)
    context.set_source_rgba(*style.color)
    context.set_line_join(style.join)
    context.set_line_cap(style.cap)

    for seg in stroke.segments:
        context.line_to(seg.x, seg.y)

    # round line join is important with thicker lines
    #context.set_line_join(cairo.LINE_JOIN_ROUND)
    # TODO: not for highlighter
    #context.set_line_cap(cairo.LINE_CAP_ROUND)
    context.stroke()

@contextmanager
def draw_context(fn):
    surface = cairo.PDFSurface(fn, WIDTH, HEIGHT)
    try:
        context = cairo.Context(surface)
        yield context
    finally:
        surface.finish()

# vim: sw=4:et:ai
