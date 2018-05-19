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

+---------------+----------+------+--------+
| Tool          | Pressure | Tilt | Brush  |
+===============+==========+======+========+
| Ballpoint     |    Y     |  N   |   Y    |
+---------------+----------+------+--------+
| Marker        |    N     |  Y   |   Y    |
+---------------+----------+------+--------+
| Fineliner     |    N     |  N   |   N    |
+---------------+----------+------+--------+
| Sharp pencil  |    N     |  N   | pencil |
+---------------+----------+------+--------+
| Tilt pencil   |  Y (1)   |  Y   |   Y    |
+---------------+----------+------+--------+
| Brush         |    Y     |  Y   |   N    |
+---------------+----------+------+--------+
| Highlighter   |    N     |  N   |   N    |
+---------------+----------+------+--------+
| Eraser        |    N     |  N   |   N    |
+---------------+----------+------+--------+
| Erase Area    |    N     |  N   |  N (3) |
+---------------+----------+------+--------+

1. Tilt pencil uses pressure to distinguish between two brush
   versions - lighter or darker.
2. Highlighter has static width of 30px.
3. Some shapes have an irregular edge, could it be due to a brush?

Use color alpha only for highlighter and eraser area. All other tools
should use appropriate brushes at full opacity. For example, drawing with
pencil in exactly the same place does not make it darker. This also allows
to draw a single stroke of varying width with multiple lines in Cairo.
Otherwise, due to line overlap, we would have to draw a stroke with an
outline and fill.

Try tilt test example from `http://www.wacomeng.com/windows/index.html` for
tilt calculations.
"""

from functools import partial
from .util import to_point

def single_line(calc, stroke):
    """
    Return collection containing single line.

    :param calc: Width calculator.
    :param stroke: Stroke data.
    """
    yield (calc(stroke), (to_point(seg) for seg in stroke.segments))

def multi_line(calc, stroke):
    """
    Return collection of lines of varying width. 

    :param calc: Width calculator.
    :param stroke: Stroke to convert to lines.
    """
    segments = stroke.segments

    # only pressure changes, so optimize by drawing lines with the same
    # pressure as single path
    lines = (
        (calc(stroke, s1), (to_point(s1), to_point(s2)))
        for s1, s2 in zip(segments[:-1], segments[1:])
    )
    yield from lines

def calc_width_fineliner(stroke):
    """
    Calculate fineliner width.

    :param stroke: Stroke data.
    """
    return 32 * stroke.width ** 2 - 116 * stroke.width + 107

def calc_width_sharp_pencil(stroke):
    """
    Calculate sharp pencil width.

    :param stroke: Stroke data.
    """
    return 16 * stroke.width - 27

def calc_width_eraser(stroke):
    """
    Calculate eraser width.

    :param stroke: Stroke data.
    """
    return 1280 * stroke.width ** 2 - 4800 * stroke.width + 4510

def calc_width_ballpoint(stroke, segment):
    """
    Calculate ballpoint width.

    :param stroke: Stroke data.
    :param segment: Segment data.
    """
    width = calc_width_fineliner(stroke)
    return width + segment.pressure ** 2048

line_ballpoint = partial(multi_line, calc_width_ballpoint)
line_fineliner = partial(single_line, calc_width_fineliner)
line_sharp_pencil = partial(single_line, calc_width_sharp_pencil)
line_highlighter = partial(single_line, lambda s: 30)
line_eraser = partial(single_line, calc_width_eraser)
line_erase_area = partial(single_line, lambda s: 1)

# vim: sw=4:et:ai
