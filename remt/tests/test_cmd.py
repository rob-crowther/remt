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
Command line commands unit tests.
"""

import os.path
from datetime import datetime

from remt import cmd as r_cmd
from remt.error import *

import asynctest
import pytest
from unittest import mock


def test_fn_path():
    """
    Test creating UUID based path from metadata.
    """
    meta = {'uuid': 'xyz'}
    result = r_cmd.fn_path(meta, base='/x/y', ext='.met')
    assert '/x/y/xyz.met' == result

def test_ls_line():
    """
    Test creating `ls` command basic output line.
    """
    result = r_cmd.ls_line('a/b', None)
    assert 'a/b' == result

@mock.patch.object(r_cmd, 'datetime')
def test_ls_line_long(mock_dt):
    """
    Test creating `ls` command long output line.
    """
    meta = {
        'pinned': True,
        'bookmarked': True,
        'type': 'CollectionType',
        'lastModified': '1526115458925',
    }
    mock_dt.fromtimestamp.return_value = datetime(2018, 5, 12, 9, 57, 38)
    result = r_cmd.ls_line_long('a/b', meta)
    assert 'db 2018-05-12 09:57:38 a/b' == result

def test_ls_filter_path():
    """
    Test `ls` command metadata filtering with parent path.
    """
    meta = {'a': 1, 'a/b': 2, 'a/c': 3, 'b': 4, 'c': 5}
    result = r_cmd.ls_filter_path(meta, 'a')
    assert {'a/b': 2, 'a/c': 3} == result

def test_ls_filter_parent_uuid():
    """
    Test `ls` command metadata filtering for items with parent identified
    by UUID.
    """
    meta = {
        'a': {'uuid': 1},
        'a/b': {'uuid': 2, 'parent': 1},
        'a/c': {'uuid': 3, 'parent': 1},
        'd': {'uuid': 4},
    }
    result = r_cmd.ls_filter_parent_uuid(meta, 1)
    expected = {
        'a/b': {'uuid': 2, 'parent': 1},
        'a/c': {'uuid': 3, 'parent': 1},
    }
    assert expected == result

def test_ls_filter_parent_uuid_null():
    """
    Test `ls` command metadata filtering for items with parent identified
    by UUID when UUID is null.
    """
    meta = {
        'a': {'uuid': 1},
        'a/b': {'uuid': 2, 'parent': 1},
        'a/c': {'uuid': 3, 'parent': 1},
        'd': {'uuid': 4},
    }
    result = r_cmd.ls_filter_parent_uuid(meta, None)

    # only items with no parents expected
    expected = {
        'a': {'uuid': 1},
        'd': {'uuid': 4},
    }
    assert expected == result

def test_read_config_error():
    """
    Test if error is raised when no `remt` configuration project is found.
    """
    with mock.patch.object(os.path, 'exists') as exists:
        exists.return_value = False

        with pytest.raises(ConfigError):
            r_cmd.read_config()

def test_norm_path():
    """
    Test path normalisation.
    """
    result = r_cmd.norm_path('a//b/c//d///')
    assert 'a/b/c/d' == result

def test_norm_path_leading_slashes():
    """
    Test path normalisation with leading slashes.
    """
    result = r_cmd.norm_path('///a//b/c//d///')
    assert 'a/b/c/d' == result

def test_fn_metadata_error():
    """
    Test if error is raised if there is no metadata for a path.
    """
    meta = {'a/b/': 1}

    with pytest.raises(FileError):
        r_cmd.fn_metadata(meta, 'x/y')

@pytest.mark.asyncio
async def test_read_meta():
    """
    Test reading metadata.
    """
    sftp = mock.MagicMock()
    sftp.mget = asynctest.CoroutineMock()
    dir_meta = 'dir'

    with mock.patch('glob.glob') as mock_glob, \
            mock.patch('json.load') as mock_json_load, \
            mock.patch('builtins.open') as mock_open:

        mock_glob.side_effect = [
            # let's make read_meta resistant to some filesystem
            # inconsistencies by introducing non-matching files
            ['f1.content', 'f2.content', 'f3.content', 'f5.content'],
            ['f1.metadata', 'f2.metadata', 'f3.metadata', 'f4.metadata'],
        ]
        mock_json_load.side_effect = [
            {'visibleName': 'f1', 'deleted': False},
            {'pages': 3},

            # deleted filename shall not be visible in the results
            {'visibleName': 'f2', 'deleted': True},
            {'pages': 4},

            {'visibleName': 'f3'},
            {'pages': 5},
            {'visibleName': 'f4'},
            {'pages': 6},
        ]
        result = await r_cmd.read_meta(sftp, dir_meta)
        assert ['f1', 'f2', 'f3'] == list(result)
        assert {'pages': 3} == result['f1']['content']
        assert {'pages': 4} == result['f2']['content']
        assert {'pages': 5} == result['f3']['content']

# vim: sw=4:et:ai
