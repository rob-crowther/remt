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

from remt import cmd as r_cmd


def test_fn_path():
    """
    Test creating UUID based path from metadata.
    """
    meta = {'uuid': 'xyz'}
    result = r_cmd.fn_path(meta, base='/x/y', ext='met')
    assert '/x/y/xyz.met' == result

# vim: sw=4:et:ai
