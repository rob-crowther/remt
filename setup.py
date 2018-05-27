#!/usr/bin/env python3
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

from setuptools import setup, find_packages

setup(
    name='remt',
    version='0.4.0',
    description='remt - reMarkable tablet command-line tools',
    author='Artur Wroblewski',
    author_email='wrobell@riseup.net',
    url='https://gitlab.com/wrobell/remt',
    setup_requires = ['setuptools_git >= 1.0',],
    packages=find_packages('.'),
    scripts=('bin/remt',),
    include_package_data=True,
    long_description=\
"""\
reMarkable tablet command-line tools.

Features

- reMarkable tablet operations

  - list files and directories
  - create directories
  - export a notebook as PDF file
  - export an annotated PDF document
  - import a PDF document
  - create index of PDF file annotations

- significantly smaller PDF files comparing to the ones exported by the
  reMarkable tablet
- export supports

  - multi-page notebooks and PDF files
  - the following drawing tools

    - ballpoint (no brush supported yet)
    - fineliner
    - sharp pencil with pencil brush
    - highlighter
    - eraser
    - erase area

- `remt` project can be used as a library for UI applications

See `project's homepage <https://gitlab.com/wrobell/remt>`_ for
usage and installation instructions.

This project is *not* an official project of the reMarkable company.

The `remt` project is licensed under terms of GPL license, version 3, see
COPYING file for details. As stated in the license, there is no warranty,
so any usage is on your own risk.

.. image:: https://gitlab.com/wrobell/remt/raw/master/examples/rm.png
   :align: center
""",
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering',
    ],
    keywords='remarkable tools',
    license='GPL',
    install_requires=[
        'pygobject', 'pycairo', 'asyncssh', 'cytoolz',
        'asyncio-contextmanager',
    ],
)

# vim: sw=4:et:ai
