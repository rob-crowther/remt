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
PDF utilities.
"""

import gi
gi.require_version('Poppler', '0.18')

import pathlib
from gi.repository import Poppler

def pdf_open(fn):
    """
    Open PDF file and return Poppler library PDF document.

    :param fn: PDF file name.
    """
    path = pathlib.Path(fn).resolve().as_uri()
    return Poppler.Document.new_from_file(path)

# vim: sw=4:et:ai
