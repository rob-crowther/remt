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

"""
PDF utilities.
"""

import gi
gi.require_version('Poppler', '0.18')

import pathlib
from gi.repository import Poppler

from . import const
from .util import to_point


def pdf_open(fn):
    """
    Open PDF file and return Poppler library PDF document.

    :param fn: PDF file name.
    """
    path = pathlib.Path(fn).resolve().as_uri()
    return Poppler.Document.new_from_file(path)

def pdf_scale(page):
    """
    Get scaling factor for a PDF page to fit reMarkable tablet vector data
    onto the page.

    :param page: Poppler PDF page object.
    """
    w, h = page.get_size()
    return max(w / const.PAGE_WIDTH, h / const.PAGE_HEIGHT)

def pdf_area(page, stroke):
    """
    Get PDF page area for a stroke.

    :param page: Poppler PDF page object.
    :param stroke: reMarkable tablet stroke data.
    """
    to_x = lambda p: to_point(p)[0]
    to_y = lambda p: to_point(p)[1]
    x1 = min(to_x(s) for s in stroke.segments)
    x2 = max(to_x(s) for s in stroke.segments)
    y1 = min(to_y(s) for s in stroke.segments)
    y2 = max(to_y(s) for s in stroke.segments)

    factor = pdf_scale(page)

    area = Poppler.Rectangle()
    area.x1 = (x1 - 15) * factor
    area.y1 = y1 * factor
    area.x2 = (x2 + 15) * factor
    area.y2 = y2 * factor
    assert area.x1 < area.x2
    assert area.y1 < area.y2

    return area

def pdf_text(page, stroke):
    """
    Having a reMarkable tablet stroke data, get text annotated by the
    stroke.

    :param page: Poppler PDF page object.
    :param stroke: reMarkable tablet stroke data.
    """
    area = pdf_area(page, stroke)
    return page.get_text_for_area(area)

# vim: sw=4:et:ai
