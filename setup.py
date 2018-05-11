#!/usr/bin/env python3
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

import sys
import os.path

from setuptools import setup, find_packages

setup(
    name='remt',
    version='0.0.1',
    description='remt - reMarkable tablet tools',
    author='Artur Wroblewski',
    author_email='wrobell@riseup.net',
    url='https://gitlab.com/wrobell/remt',
    setup_requires = ['setuptools_git >= 1.0',],
    packages=find_packages('.'),
    scripts=('bin/remt',),
    include_package_data=True,
    long_description=\
"""\
reMarkable tablet tools

- list device files
- put a PDF file onto a device
- get notes and annotated PDF documents
""",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
    ],
    keywords='remarkable tools',
    license='GPL',
    install_requires=['pycairo', 'asyncssh'],
)

# vim: sw=4:et:ai
