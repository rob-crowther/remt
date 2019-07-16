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
reMarkable table lines parser unit tests.
"""

import io
import remt.parser as r_parser

def test_parse_item():
    """
    Test parsing of a drawing item.
    """
    # add some trailing bytes, which shall be not read
    data = io.BytesIO(b'\x01\x02\x03\x04\x00\xff')
    result = r_parser.parse_item(r_parser.FMT_LAYER, data)
    assert (0x04030201,) == result

    # still possible to read the rest of the data
    remaining = data.read()
    assert b'\x00\xff' == remaining

# vim: sw=4:et:ai
