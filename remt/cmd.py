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

"""
Command line commands.
"""

import asyncssh
import configparser
import glob
import json
import os.path
import shutil
from aiocontext import async_contextmanager
from datetime import datetime
from collections import namedtuple
from tempfile import TemporaryDirectory
from cytoolz.dicttoolz import assoc, get_in
from cytoolz.functoolz import flip, curry
from uuid import uuid4 as uuid

import remt
from .data import Page, Stroke
from .error import *
from .util import split
from .pdf import pdf_open, pdf_text


BASE_DIR = '/home/root/.local/share/remarkable/xochitl'

FILE_TYPE = {
    'CollectionType': 'd',
}

ERROR_CFG = """\
Configuration file {conf} not found

  Create configuration file `{conf}` with contents

    [connection]
    host=10.11.99.1
    user=root
    password=<your reMarkable tablet password>
"""


# config: remt config
# sftp: SFTP connection to a device
# dir_meta: metadata files
# meta: parsed metadata
# dir_data: directory where to fetch files from a device or where to
#   prepare files for upload
RemtContext = namedtuple(
    'RemtContext',
    ['config', 'sftp', 'dir_meta', 'meta', 'dir_data'],
)

#
# utilities
#

def read_config():
    """
    Read and return `remt` project configuration.
    """
    conf_file = os.path.expanduser('~/.config/remt.ini')
    if not os.path.exists(conf_file):
        msg = ERROR_CFG.format(conf=conf_file)
        raise ConfigError(msg)

    cp = configparser.ConfigParser()
    cp.read(conf_file)
    return cp

@async_contextmanager
async def remt_ctx():
    """
    Create a `remt` project context.

    The function is an asynchronous context manager.
    """
    config = read_config()

    host = config.get('connection', 'host')
    user = config.get('connection', 'user')
    password = config.get('connection', 'password')

    try:
        async with asyncssh.connect(host, username=user, password=password) as conn:
            async with conn.start_sftp_client() as sftp:
                with TemporaryDirectory() as dir_base:
                    dir_meta = os.path.join(dir_base, 'metadata')
                    dir_data = os.path.join(dir_base, 'data')
                    os.mkdir(dir_meta)
                    os.mkdir(dir_data)

                    meta = await read_meta(sftp, dir_meta)
                    yield RemtContext(config, sftp, dir_meta, meta, dir_data)
    except OSError as ex:
        if ex.errno == 101:
            raise ConnectionError(
                'Cannot connect to a reMarkable tablet: {}'.format(ex.strerror)
            )
        else:
            raise

def fn_path(data, base=BASE_DIR, ext='*'):
    """
    Having metadata object create UUID based path of a file created by
    reMarkable tablet.

    :param data: Metadata object.
    """
    return '{}/{}.{}'.format(base, data['uuid'], ext)

def norm_path(path):
    """
    Normalise path of a file on a reMarkable tablet.

    All leading and trailing slashes are removed. Multiple slashes are
    replaced with one.

    :param path: Path to normalise.
    """
    return os.path.normpath(path).strip('/')

def fn_metadata(meta, path):
    """
    Get reMarkable tablet file metadata or raise file not found error if no
    metadata for path is found.

    :param meta: reMarkable tablet metadata.
    :param path: Path of reMarkable tablet file.
    """
    data = meta.get(path)
    if not data:
        raise FileError('File or directory not found: {}'.format(path))
    return data

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

def create_metadata(is_dir, parent_uuid, name):
    now = datetime.utcnow()
    tstamp = int(now.timestamp() * 1000)
    type = 'CollectionType' if is_dir else 'DocumentType'
    data = {
        'deleted': False,
        'lastModified': str(tstamp),
        'metadatamodified': True,
        'modified': True,
        'parent': parent_uuid,
        'pinned': False,
        'synced': False,
        'type': type,
        'version': 0,
        'visibleName': name,
    }
    return data

async def read_meta(sftp, dir_meta):
    """
    Read metadata from a reMarkable tablet.
    """
    await sftp.mget(BASE_DIR + '/*.metadata', dir_meta)

    files = glob.glob(dir_meta + '/*.metadata')
    data = (json.load(open(fn)) for fn in files)
    data = (v for v in data if not v.get('deleted'))

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

    tstamp = int(data['lastModified']) / 1000
    tstamp = datetime.fromtimestamp(tstamp)

    line = '{}{} {:%Y-%m-%d %H:%M:%S} {}'.format(is_dir, bookmarked, tstamp, fn)
    return line

def ls_filter_path(meta, path):
    """
    Filter metadata to keep metadata starting with path name.

    The path name itself *is* filtered out.

    :param meta: reMarkable tablet metadata.
    :param path: Path name.
    """
    meta = {k: v for k, v in meta.items() if k.startswith(path) and path != k}
    return meta

def ls_filter_parent_uuid(meta, uuid):
    """
    Filter metadata to keep metadata starting, which parent is identified
    by UUID.

    :param meta: reMarkable tablet metadata.
    :param uuid: UUID of parent directory.
    """
    check = lambda v: not v if uuid is None else v == uuid
    meta = {k: v for k, v in meta.items() if check(v.get('parent'))}
    return meta

async def cmd_ls(args):
    to_line = ls_line_long if args.long else ls_line
    path = norm_path(args.path) if args.path else None

    async with remt_ctx() as ctx:
        meta = ctx.meta

        # get starting UUID while we have all metadata
        start = None
        if path:
            start = fn_metadata(meta, path)['uuid']

        if path:
            meta = ls_filter_path(meta, path)

        if not args.recursive:
            meta = ls_filter_parent_uuid(meta, start)

        lines = (to_line(k, v) for k, v in sorted(meta.items()))
        print('\n'.join(lines))

#
# cmd: mkdir
#

async def cmd_mkdir(args):
    """
    Create a directory on reMarkable tablet device.
    """
    async with remt_ctx() as ctx:
        meta = ctx.meta
        path = norm_path(args.path)

        if path in meta:
            msg = 'Cannot create directory "{}" as it exists'.format(path)
            raise FileError(msg)

        parent, name = os.path.split(path)
        if parent and parent not in meta:
            raise FileError('Parent directory not found')

        assert bool(name)

        parent_uuid = get_in([parent, 'uuid'], meta)
        data = create_metadata(True, parent_uuid, name)

        dir_fn = os.path.join(ctx.dir_data, str(uuid()))

        with open(dir_fn + '.metadata', 'w') as f:
            json.dump(data, f)

        # empty content file required to create a directory
        with open(dir_fn + '.content', 'w') as f:
            json.dump({}, f)

        await ctx.sftp.mput(dir_fn + '.*', BASE_DIR)

#
# cmd: export
#

async def cmd_export(args):
    path = norm_path(args.input)

    async with remt_ctx() as ctx:
        data = fn_metadata(ctx.meta, path)

        to_copy = fn_path(data)
        await ctx.sftp.mget(to_copy, ctx.dir_data, recurse=True)

        fin = fn_path(data, base=ctx.dir_data, ext='lines')
        fin_pdf = fn_path(data, base=ctx.dir_data, ext='pdf')
        fin_pdf = fin_pdf if os.path.exists(fin_pdf) else None
        with open(fin, 'rb') as f, \
                remt.draw_context(fin_pdf, args.output) as ctx:

            for item in remt.parse(f):
                remt.draw(item, ctx)

#
# cmd: import
#
def _prepare_import_data(ctx, fn_in, out_uuid):
    """
    Prepare import data for a file to be uploaded onto a reMarkable
    tablet.

    :param ctx: `remt` project context.
    :param fn_in: File to be imported.
    :param out_uuid: UUID of the output directory located on a reMarkable
        tablet.
    """
    name = os.path.basename(fn_in)
    fn_base = os.path.join(ctx.dir_data, str(uuid()))
    data = create_metadata(False, out_uuid, name)

    fn_pdf = fn_base + '.pdf'
    shutil.copy(fn_in, fn_pdf)
    with open(fn_base + '.metadata', 'w') as f:
        json.dump(data, f)

    # empty content file required
    with open(fn_base + '.content', 'w') as f:
        page_count = pdf_open(fn_pdf).get_n_pages()
        content = {
            'fileType': 'pdf',
            'lastOpenedPage': 0,
            'lineHeight': -1,
            'pageCount': page_count,

        }
        json.dump(content, f)
    return fn_base + '.*'

async def cmd_import(args):
    """
    Import a number of files onto a directory on a reMarkable tablet.
    """
    output = norm_path(args.output)

    async with remt_ctx() as ctx:
        out_meta = fn_metadata(ctx.meta, output)
        if out_meta['type'] != 'CollectionType':
            raise FileError('Destination path is not a directory')

        out_uuid = out_meta['uuid']
        to_import = [
            _prepare_import_data(ctx, fn, out_uuid) for fn in args.input
        ]
        await ctx.sftp.mput(to_import, BASE_DIR)

#
# cmd: index
#

async def cmd_index(args):
    to_text = curry(pdf_text)
    is_item = flip(isinstance, (Page, Stroke))
    is_page = flip(isinstance, Page)

    fmt_header = lambda p: \
        '#. Page {} ({})\n'.format(p.get_label(), p.get_index())
    fmt_text = '   * ``{}``'.format

    path = norm_path(args.input)

    async with remt_ctx() as ctx:
        data = fn_metadata(ctx.meta, path)

        to_copy = fn_path(data)
        await ctx.sftp.mget(to_copy, ctx.dir_data, recurse=True)

        fin = fn_path(data, base=ctx.dir_data, ext='lines')
        fin_pdf = fn_path(data, base=ctx.dir_data, ext='pdf')
        with open(fin, 'rb') as f:
            pdf_doc = pdf_open(fin_pdf)
            get_page = pdf_doc.get_page

            items = remt.parse(f)
            # find pages and strokes
            items = (v for v in items if is_item(v))
            # split into (page, strokes)
            items = split(is_page, items)
            # get PDF pages
            items = ((get_page(p.number), s) for p, s in items)
            # for each page and stroke get text under stroke
            items = ((p, map(to_text(p), s)) for p, s in items)
            # page header and each highlighted text formatted
            items = ((fmt_header(p), map(fmt_text, t)) for p, t in items)
            for header, texts in items:
                print(header)
                for text in texts:
                    print(text)
                print()

COMMANDS = {
    'ls': cmd_ls,
    'mkdir': cmd_mkdir,
    'export': cmd_export,
    'import': cmd_import,
    'index': cmd_index,
}

# vim: sw=4:et:ai
