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
Various line drawing strategies.

1. Marker is tilt dependent.

2. Tilt pencil

- pressure changes between two brush versions - lighter or darker
- tilt dependent
"""

def draw_line_multi(cr, stroke, style):
    """
    Draw a line varying width with multiple paths.

    :param cr: Cairo context.
    :param stroke: Stroke data.
    :param style: Style data.
    """
    segments = stroke.segments
    for s1, s2 in zip(segments[:-1], segments[1:]):
        cr.new_path()

        # only pressure changes, so optimize by drawing lines with the same
        # pressure as single path
        width = style.width
        width += s1.pressure ** 2048

        cr.set_line_width(width)
        cr.move_to(s1.x, s1.y)
        cr.line_to(s2.x, s2.y)
        cr.stroke()

def draw_line_single(cr, stroke, style):
    """
    Draw a line with single path.

    :param cr: Cairo context.
    :param stroke: Stroke data.
    :param style: Style data.
    """
    cr.new_path()
    cr.set_line_width(style.width)
    for seg in stroke.segments:
        cr.line_to(seg.x, seg.y)
    cr.stroke()

# vim: sw=4:et:ai
