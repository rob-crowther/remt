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
Drawing tool unit tests.
"""

from remt import tool
from remt.data import Stroke, Segment, Style

def test_single_line():
    """
    Test calculation of a single line.
    """
    stroke = Stroke(
        0, 0, 0, 0,
        [
            Segment(0, 0, 0, 0, 0, 0),
            Segment(0, 1, 1, 0, 0, 0),
            Segment(0, 2, 2, 0, 0, 0),
        ]
    )
    style = Style(10, 0, 0, 0, 0, 0)

    result = tool.single_line(stroke, style)
    width, points = next(result)

    # no more lines
    assert next(result, None) is None
    assert 10 == width
    assert [(0, 0), (1, 1), (2, 2)] == list(points)

def test_multi_line():
    """
    Test calculation of a multi line.
    """
    stroke = Stroke(
        0, 0, 0, 0,
        [
            Segment(0, 0, 0, 1, 0, 0),
            Segment(0, 1, 1, 2, 0, 0),
            Segment(0, 2, 2, 3, 0, 0),
        ]
    )
    style = Style(10, 0, 0, 0, 0, 0)

    calc = lambda st, seg: st.width ** seg.pressure
    l1, l2 = tool.multi_line(calc, stroke, style)

    assert (10, ((0, 0), (1, 1))) == l1
    assert (100, ((1, 1), (2, 2))) == l2

# vim: sw=4:et:ai
