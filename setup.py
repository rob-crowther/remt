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

- list files on a reMarkable tablet
- put a PDF file onto a reMarkable tablet
- export a notebook or an annotated PDF document from a reMarkable tablet
""",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia :: Graphics :: Vector-Based',
        'Topic :: Scientific/Engineering',
    ],
    keywords='remarkable tools',
    license='GPL',
    install_requires=['pygobject', 'pycairo', 'asyncssh', 'cytoolz'],
)

# vim: sw=4:et:ai
