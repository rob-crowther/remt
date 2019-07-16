#!/usr/bin/env python3
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

import ast
from setuptools import setup, find_packages

VERSION = ast.parse(
    next(l for l in open('remt/__init__.py') if l.startswith('__version__'))
).body[0].value.s

setup(
    name='remt',
    version=VERSION,
    description='remt - reMarkable tablet command-line tools',
    author='Artur Wroblewski',
    author_email='wrobell@riseup.net',
    url='https://gitlab.com/wrobell/remt',
    project_urls={
        'Code': 'https://gitlab.com/wrobell/remt',
        'Issue tracker': 'https://gitlab.com/wrobell/remt/issues',
    },
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
  - export a notebook as PDF file using reMarkable tablet renderer or remt
    project renderer
  - export an annotated PDF document using reMarkable tablet renderer or remt
    project renderer
  - import a PDF document
  - create index of PDF file annotations

- `remt` project renderer supports large files export and usually produces
  smaller PDF files comparing to the reMarkable tablet renderer
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

Please use reMarkable firmware version 1.7.2.3 or later.

The `remt` project is licensed under terms of GPL license, version 3, see
COPYING file for details. As stated in the license, there is no warranty,
so any usage is on your own risk.

.. image:: https://gitlab.com/wrobell/remt/raw/master/examples/rm.png
   :align: center
""",
    long_description_content_type='text/x-rst',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering',
    ],
    keywords='remarkable tools',
    license='GPLv3+',
    install_requires=[
        'pygobject', 'pycairo', 'asyncssh', 'cytoolz',
        'asyncio-contextmanager',
    ],
)

# vim: sw=4:et:ai
