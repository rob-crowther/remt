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
Command line commands.
"""

import asyncssh
import configparser
import glob
import json
import os
import os.path
from tempfile import TemporaryDirectory
from cytoolz.dicttoolz import assoc

import remt


BASE_DIR = '/home/root/.local/share/remarkable/xochitl'

FILE_TYPE = {
    'CollectionType': 'd',
}

#
# utilities
#

def fn_path(data, base=BASE_DIR, ext='*'):
    """
    Having metadata object create UUID based path of a file created by
    reMarkable tablet.

    :param data: Metadata object.
    """
    return '{}/{}.{}'.format(base, data['uuid'], ext)

async def fetch(source, target):
    """
    Fetch files from a reMarkable tablet into a local directory.

    :param source: Files to be fetched from a reMarkable tablet.
    :param target: Local directory name.
    """
    conf_file = os.path.join(os.environ['HOME'], '.config', 'remt.ini')
    cp = configparser.ConfigParser()
    cp.read(conf_file)

    host = cp.get('connection', 'host')
    user = cp.get('connection', 'user')
    password = cp.get('connection', 'password')

    ctx = asyncssh.connect(host, username=user, password=password)
    async with ctx as conn:
        async with conn.start_sftp_client() as sftp:
            await sftp.mget(source, target, recurse=True)

#
# metadata
#

def to_path(data, meta):
    parent = data.get('parent')
    name = data['visibleName']
    if parent:
        return to_path(meta[parent], meta) + '/' + name
    else:
        return name
        
def resolve_uuid(meta):
    meta = {k: assoc(v, 'uuid', k) for k, v in meta.items()}
    return {to_path(data, meta): data for data in meta.values()}

async def read_meta():
    """
    Read metadata from a reMarkable tablet.
    """
    with TemporaryDirectory() as dest:
        await fetch(BASE_DIR + '/*.metadata', dest)

        files = glob.glob(dest + '/*.metadata')
        data = (json.load(open(fn)) for fn in files)

        uuids = (os.path.basename(v) for v in files)
        uuids = (os.path.splitext(v)[0] for v in uuids)
        meta = {fn: v for fn, v in zip(uuids, data)}
        return resolve_uuid(meta)

#
# cmd: ls
#

def marker(cond, marker):
    return marker if cond else '-'

def ls_line(fn, data):
    """
    Create `ls` command basic output line.
    """
    return fn

def ls_line_long(fn, data):
    """
    Create `ls` command long output line.
    """
    bookmarked = marker(data['pinned'] is True, 'b')
    is_dir = marker(data['type'] == 'CollectionType', 'd')
    line = '{}{} {}'.format(is_dir, bookmarked, fn)
    return line

async def cmd_ls(options):
    meta = await read_meta()
    to_line = ls_line_long if options.long else ls_line
    lines = (to_line(k, v) for k, v in sorted(meta.items()))
    print('\n'.join(lines))

#
# cmd: get
#

async def cmd_get(args):
    meta = await read_meta()
    with TemporaryDirectory() as dest:
        data = meta[args.input]  # TODO: handle non-existing file nicely

        to_copy = fn_path(data)
        await fetch(to_copy, dest)

        fin = fn_path(data, base=dest, ext='lines')
        fin_pdf = fn_path(data, base=dest, ext='pdf')
        fin_pdf = fin_pdf if os.path.exists(fin_pdf) else None
        with open(fin, 'rb') as f, \
                remt.draw_context(fin_pdf, args.output) as ctx:

            for item in remt.parse(f):
                remt.draw(item, ctx)
         
# vim: sw=4:et:ai
