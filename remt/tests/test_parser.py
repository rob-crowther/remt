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
reMarkable table lines parser unit tests.
"""

import remt.parser as r_parser

def test_inject_into_none():
    """
    Test injecting into a stream of items when nothing to do.
    """
    items = [1, 2, 3, 4, 5]
    result = r_parser.inject_into(int.__eq__, None, items)
    result = list(result)
    assert [1, 2, 3, 4, 5] == result

def test_inject_into():
    """
    Test injecting into a stream of items.
    """
    items = [1, 2, 3, 3, 4, 5]
    inject = lambda v1, v2: [v1, -1]
    result = r_parser.inject_into(int.__eq__, inject, items)
    result = list(result)
    assert [1, 2, 3, -1, 3, 4, 5] == result

# vim: sw=4:et:ai
