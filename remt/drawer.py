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

import gi
gi.require_version('Poppler', '0.18')

import cairo
import io
import logging
import os.path
import pathlib
import pkgutil
from collections import namedtuple
from contextlib import contextmanager
from functools import singledispatch, lru_cache, partial
from gi.repository import Poppler

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
    None,
)

STYLE_HIGHLIGHTER = Style(
    30,
    COLOR_HIGHLIGHTER,
    cairo.LINE_JOIN_ROUND,
    cairo.LINE_CAP_SQUARE,
    None
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
    # Ballpoint
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
        None,
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
        None,
    ),
    # Pencil - Sharp
    7: lambda st: Style(
        16 * st.width - 27,
        COLOR_STROKE[st.color],
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
        'pencil.png',
    ),
    # Erase area
    8: lambda st: Style(
        st.width,
        COLOR_STROKE[st.color]._replace(alpha=0),
        cairo.LINE_JOIN_ROUND,
        cairo.LINE_CAP_ROUND,
        None,
    ),
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
        factor = max(w / WIDTH, h / HEIGHT)
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
    f = STYLE.get(stroke.pen)
    if f is not None:
        style = f(stroke)
    else:
        logger.debug('Not supported pen for stroke: {}'.format(stroke))
        return

    # on new path, the position of point is undefined and first `line_to`
    # call acts as `move_to`
    cr = context.cr_ctx
    cr.save()
    cr.new_path()

    cr.set_line_width(style.width)
    cr.set_source_rgba(*style.color)
    cr.set_line_join(style.join)
    cr.set_line_cap(style.cap)

    for seg in stroke.segments:
        cr.line_to(seg.x, seg.y)

    if style.brush:
        brush = load_brush(style.brush)
        cr.set_source(brush)

    cr.stroke()
    cr.restore()

@contextmanager
def draw_context(fn_pdf, fn_out):
    factor = 1

    pdf_doc = None
    if fn_pdf:
        pdf_path = pathlib.Path(fn_pdf).resolve().as_uri()
        pdf_doc = Poppler.Document.new_from_file(pdf_path)

    surface = cairo.PDFSurface(fn_out, WIDTH, HEIGHT)
    try:
        cr_ctx = cairo.Context(surface)
        context = Context(surface, cr_ctx, pdf_doc)
        yield context
    finally:
        surface.finish()

# vim: sw=4:et:ai
