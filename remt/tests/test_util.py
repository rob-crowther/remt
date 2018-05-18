
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
Unit tests for `remt` project utilities.
"""

from cytoolz.functoolz import flip

from remt.util import split

def test_split():
    """
    Test splitting sequence by a function key.
    """
    items = [
        'a', 1, 2, 3,
        'b', 5, 6, 7, 8,
        'c', 4, 3,
        'd',
        'e', 1, 2, 3, 4,
    ]

    is_str = flip(isinstance, str)
    result = split(is_str, items)
    expected = [
        ('a', (1, 2, 3)),
        ('b', (5, 6, 7, 8)),
        ('c', (4, 3)),
        ('e', (1, 2, 3, 4)),
    ]

    assert expected == list(result)

# vim: sw=4:et:ai
