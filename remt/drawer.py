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
reMarkable strokes drawing using Cairo library.
"""

import cairo
import io
import logging
import os.path
import pkgutil
from collections import namedtuple
from contextlib import contextmanager
from functools import singledispatch, lru_cache, partial

from . import const, tool
from .data import *
from .pdf import pdf_open, pdf_scale

logger = logging.getLogger(__name__)

COLOR_STROKE = {
    0: Color(0, 0, 0, 1),
    1: Color(0.5, 0.5, 0.5, 1),
    2: Color(1, 1, 1, 1),
}

COLOR_HIGHLIGHTER = Color(1.0, 0.8039, 0.0, 0.1)

STYLE_DEFAULT = Style(
    None,
    cairo.LINE_JOIN_ROUND,
    cairo.LINE_CAP_ROUND,
    None,
    tool.single_line,
)

STYLE_HIGHLIGHTER = Style(
    COLOR_HIGHLIGHTER,
    cairo.LINE_JOIN_ROUND,
    cairo.LINE_CAP_SQUARE,
    None,
    tool.line_highlighter,
)

STYLE_ERASER = Style(
    COLOR_STROKE[2],
    cairo.LINE_JOIN_ROUND,
    cairo.LINE_CAP_ROUND,
    None,
    tool.line_eraser,
)

style_default = STYLE_DEFAULT._replace

STYLE = {
# brush, pencil tilt and marker - tilt dependent
#0: lambda st: Style(
#    (5 * st.tilt) * (6 * st.width - 10) * (1 + 2 * st.pressure ** 3),
#    COLOR_STROKE[st.color],
#    cairo.LINE_JOIN_ROUND,
#    cairo.LINE_CAP_ROUND,
#),
    # Tilt pencil
#1: lambda st: STYLE_DEFAULT._replace(
#    width=(8 * st.width - 14),
#    color=COLOR_STROKE[st.color],
#    cap=cairo.LINE_CAP_BUTT,
#    brush='pencil.png',
#    tool_line=tool.multi_line,
#),
    # Marker (tilt dependent)
#3: lambda st: STYLE_DEFAULT._replace(
#    width=64 * st.width - 112,
#    color=COLOR_STROKE[st.color],
#    brush=None,
#    tool_line=tool.multi_line,
#),
    # Ballpoint
    2: style_default(tool_line=tool.line_ballpoint),

    # Fineliner
    4: style_default(tool_line=tool.line_fineliner),

    # Highlighter
    5: STYLE_HIGHLIGHTER,

    # Eraser
    6: STYLE_ERASER,

    # Sharp pencil
    7: style_default(tool_line=tool.line_sharp_pencil, brush='pencil.png'),

    # Erase area
    8: STYLE_ERASER._replace(tool_line=tool.line_erase_area),
}


path_brush = partial(os.path.join, 'brush')

@lru_cache(maxsize=4)
def load_brush(fn):
    data = pkgutil.get_data('remt', path_brush(fn))
    img = cairo.ImageSurface.create_from_png(io.BytesIO(data))
    brush = cairo.SurfacePattern(img)
    brush.set_extend(cairo.EXTEND_REPEAT)
    return brush

@singledispatch
def draw(item, context):
    raise NotImplementedError('Unknown item to draw: {}'.format(item))

@draw.register(Page)
def _(page, context):
    surface = context.cr_surface
    if page.number:
        surface.show_page()

    if context.pdf_doc:
        # get page and set size of the current page of the cairo surface
        pdf_page = context.pdf_doc.get_page(page.number)
        w, h = pdf_page.get_size()
        surface.set_size(w, h)

        cr = context.cr_ctx
        # render for printing to keep the quality of the document
        pdf_page.render_for_printing(cr)

        # render remarkable lines data at scale to fit the document
        cr.save()  # to be restored at page end
        factor = pdf_scale(pdf_page)
        cr.scale(factor, factor)

@draw.register(PageEnd)
def _(page, context):
    if context.pdf_doc:
        context.cr_ctx.restore()

@draw.register(Layer)
def _(layer, context):
    pass

@draw.register(Stroke)
def _(stroke, context):
    style = STYLE.get(stroke.pen)
    if not style:
        logger.debug('Not supported pen for stroke: {}'.format(stroke))
        return

    # if no predefined style color, then use stroke color
    assert stroke.color in (0, 1, 2)
    color = style.color
    color = COLOR_STROKE[stroke.color] if color is None else color

    cr = context.cr_ctx
    cr.save()

    draw_stroke = partial(draw_fill, cr) if stroke.pen == 8 else cr.stroke

    cr.set_source_rgba(*color)
    cr.set_line_join(style.join)
    cr.set_line_cap(style.cap)

    if style.brush:
        brush = load_brush(style.brush)
        cr.set_source(brush)

    lines = style.tool_line(stroke)
    draw_multi_line(cr, draw_stroke, lines)

    cr.restore()

def draw_multi_line(cr, draw_stroke, lines):
    """
    Draw multiple lines.

    A line is tuple

    - width of a line
    - collection of points

    :param cr: Cairo context.
    :param draw_stroke: Drawing stroke function (i.e. line or filled area).
    :param lines: Collection of lines to draw.
    """
    for width, points in lines:
        # on new path, the position of point is undefined and first
        # `line_to` call acts as `move_to`
        cr.new_path()
        cr.set_line_width(width)
        for x, y in points:
            cr.line_to(x, y)
        draw_stroke()

def draw_fill(cr):
    """
    Draw Cairo shape and fill.
    """
    cr.close_path()
    cr.fill()

@contextmanager
def draw_context(fn_pdf, fn_out):
    pdf_doc = pdf_open(fn_pdf) if fn_pdf else None
    surface = cairo.PDFSurface(fn_out, const.PAGE_WIDTH, const.PAGE_HEIGHT)
    try:
        cr_ctx = cairo.Context(surface)
        context = Context(surface, cr_ctx, pdf_doc)
        yield context
    finally:
        surface.finish()

# vim: sw=4:et:ai
