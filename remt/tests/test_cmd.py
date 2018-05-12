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
Command line commands unit tests.
"""

from remt import cmd as r_cmd


def test_fn_path():
    """
    Test creating UUID based path from metadata.
    """
    meta = {'uuid': 'xyz'}
    result = r_cmd.fn_path(meta, base='/x/y', ext='met')
    assert '/x/y/xyz.met' == result

def test_ls_line():
    """
    Test creating `ls` command basic output line.
    """
    result = r_cmd.ls_line('a/b', None)
    assert 'a/b' == result

def test_ls_line_long():
    """
    Test creating `ls` command long output line.
    """
    meta = {
        'pinned': True,
        'bookmarked': True,
        'type': 'CollectionType',
    }
    result = r_cmd.ls_line_long('a/b', meta)
    assert 'db a/b' == result

# vim: sw=4:et:ai
