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
Drawing tool calculations.

Drawing tools characteristics is as follows

1. Ballpoint

- uses pressure
- does not use tilt
- uses a brush

2. Marker

- does not use pressure
- uses tilt
- uses a brush

3. Fineliner

- does not use pressure
- does not use tilt
- does not use brush

4. Sharp pencil

- does not use pressure
- does not use tilt
- uses a brush

5. Tilt pencil

- uses pressure to distinguish between two brush versions - lighter or
  darker
- uses tilt
- uses a brush

6. Brush

- uses pressure
- uses tilt
- does not use brush

Use color alpha only for highlighter and eraser area. All other tools
should use appropriate brushes at full opacity. For example, drawing with
pencil in exactly the same place does not make it darker.
"""

from functools import partial
from operator import attrgetter

point = attrgetter('x', 'y')

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

        width = style.width
        width += s1.pressure ** 2048

        cr.set_line_width(width)
        cr.move_to(s1.x, s1.y)
        cr.line_to(s2.x, s2.y)
        cr.stroke()

def single_line(stroke, style):
    """
    Return collection containing single line.

    :param stroke: Stroke data.
    :param style: Style data.
    """
    yield (style.width, (point(seg) for seg in stroke.segments))

def multi_line(calc, stroke, style):
    """
    Return collection of lines of varying width. 

    :param calc: Width calculator.
    :param stroke: Stroke to convert to lines.
    :param style: Stroke style information.
    """
    segments = stroke.segments

    # only pressure changes, so optimize by drawing lines with the same
    # pressure as single path
    lines = (
        (calc(style, s1), (point(s1), point(s2)))
        for s1, s2 in zip(segments[:-1], segments[1:])
    )
    yield from lines

def calc_width_ballpoint(style, segment):
    """
    Calculate ballpoint width.

    :param style: Stroke style information.
    :param segment: Segment data.
    """
    return style.width + segment.pressure ** 2048

multi_line_ballpoint = partial(multi_line, calc_width_ballpoint)

# vim: sw=4:et:ai
