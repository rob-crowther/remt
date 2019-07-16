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

class RemtError(Exception):
    """
    Basic class for `remt` project exceptions.
    """

class ConnectionError(RemtError):
    """
    reMarkable tablet connection error.
    """

class ConfigError(RemtError):
    """
    `remt` project configuration exception.
    """

class FileError(RemtError):
    """
    File and directory exceptions.
    """

# vim: sw=4:et:ai
