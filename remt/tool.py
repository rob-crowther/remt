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

7. Highlighter

- static width of 30px
- does not use pressure
- does not use tilt
- does not use brush

8. Eraser

- does not use pressure
- does not use tilt
- does not use brush

Use color alpha only for highlighter and eraser area. All other tools
should use appropriate brushes at full opacity. For example, drawing with
pencil in exactly the same place does not make it darker.
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
line_highlighter = partial(single_line, lambda *args: 30)
line_eraser = partial(single_line, calc_width_eraser)

# vim: sw=4:et:ai
