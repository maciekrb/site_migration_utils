#!/usr/bin/env python -u
# -*- coding:utf8 -*-
# 
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at 
# 
#     http://www.apache.org/licenses/LICENSE-2.0 
# 
# Unless required by applicable law or agreed to in writing, software 
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 
# 
# Maciek Ruckgaber <maciekrb@gmail.com> 

"""
These utils were created as general utilities to migrate web based apps
that don't have a nice and clean way to migration.

Messy things as file name identification and sanitization, db record updates
for paths with embed urls and such disasters are covered by these tools.

The tools do not modify anything, just generate code to be executed, either
via shell or sql scripts. The following are the modes of operation:

  - --sanitize: This case searches all files within a given folder, with 
    names that are not very nice to be used as urls. Actions inclued in this
    mode of operation are:
      - --filesystem: Generates shell script lines to be reviewed and executed
        to move the ugly paths into sanitized ones.
      - --database: Generates SQL script with updates of relevant rows and
        columns replacing ugly paths with sanitized ones.

  - --updateurl: This case updates a given domain name with a new one.
"""

import argparse
import logging
import sys
import HTMLParser
from subprocess import Popen, PIPE
from sitetools.dbutils import DBExpressionFinder
from sitetools.shutils import ShellScriptUtil
from sitetools.utils import convert_to_utf8
from sitetools.utils import sanitize_path
from sitetools.utils import SEPARATOR


def find_non_sanitized_files_in_path(path):
  res = Popen(
    ['find', path, '-type','f','-regex','.*[^a-zA-Z0-9_\.\/-].*','-print'], 
    stdout=PIPE,
    stderr=PIPE)
  return res.stdout

def read_non_sanitized_files_from_file(file_path):
  with open(file_path) as res:
    for f in res:
      yield f

def parse_table_layout(layout):
  if layout.count(':') != 2:
    print "Table layout does not match table_name:id:col1,col2,col3"
    sys.exit(1)

  tbl, id_col, cols = layout.split(":")
  columns = cols.split(",") if cols.find(',') else [cols]
  return (tbl.strip(), [ c.strip() for c in columns ], id_col.strip())

def _process_entry(path, html_parser):
  path = path.strip()
  path = path[2:] if path.startswith('.'+SEPARATOR) else path
  utf8_path = convert_to_utf8(path)
  unescaped = html_parser.unescape(utf8_path)
  sanitized = sanitize_path(unescaped)
  logging.debug("==FRM>[%s]" % unescaped)
  logging.debug(" +=TO>[%s]" % sanitized)
  return path, sanitized

def sanitize_entries(entries, dbuser=None, dbpass=None, dbname=None, dbhost=None, tbl_layout=None):

  # Init HTML Entity parser
  html_parser = HTMLParser.HTMLParser()

  if dbuser and dbpass and dbname:
    """ Database info provided, so try the --database script generation """

    dbref = DBExpressionFinder(dbuser, dbpass, dbname, dbhost)
    if tbl_layout.find('|'):
      for layout in tbl_layout.split('|'):
        dbref.register_target(*parse_table_layout(layout))
    else:
      dbref.register_target(*parse_table_layout(tbl_layout))

    for r in entries:
      original, sanitized = _process_entry(r, html_parser)
      upd = dbref.get_update_statements(original, sanitized)
      if upd: yield upd
      
  else:
    """ No database info available, generate filesystem scripts """
    shtool = ShellScriptUtil()
    for r in entries:
      original, sanitized = _process_entry(r, html_parser)
      shln = shtool.get_move_statements(original, sanitized)
      if shln: yield shln

def main():
  parser = argparse.ArgumentParser(description="Command line utils for website migration")

  """ modes of operation """
  parser.add_argument('--sanitize', action="store_true", help="""
    Sanitize mode, will search for ugly path in the given folder and try to nice them out.
  """)
  parser.add_argument('--updateurl', action="store_true", help="""
    Update URL mode, will generate scripts to update from a source url to a target url.
  """)

  """ mode options """
  """ Sanitization mode """
  parser.add_argument('-d', '--directory', help="Base directory to search for ugly files")
  parser.add_argument('-f', '--file', help="Reads file paths from file, one per line")

  parser.add_argument('--filesystem', action="store_true", help="Generates shell scripts to move paths")
  parser.add_argument('--database', action="store_true", help="Generates SQL scripts to update DB")
  parser.add_argument('--host', help="Database host to connect", default='localhost')
  parser.add_argument('-u', '--user', help="Database user")
  parser.add_argument('-p', '--pwd', help="Database password")
  parser.add_argument('-n', '--dbname', help="Database name")
  parser.add_argument('-t', '--tlayout', help="""
    Table layout as follows: table_name:id:co1,col2,col3  where id is a row unique id and col1,
    col2 and col3 are the columns in which the expression will be searched""")

  """ Other options """
  parser.add_argument('-v', '--verbosity', help="Verbosity level", 
      choices=['WARN','INFO','DEBUG'])

  args = parser.parse_args()

  if args.verbosity:
    logging.basicConfig(stream=sys.stderr, level=getattr(logging, args.verbosity))

  if args.sanitize:
    if args.database:
      if not (args.user and args.pwd and  args.dbname and args.tlayout):
        print "--databse option required -u -p -n  and -t options to be set"
        sys.exit(1)

    if args.directory:
      entries = find_non_sanitized_files_in_path(args.directory)
    elif args.file:
      entries = read_non_sanitized_files_from_file(args.file)
    else:
      print """ --sanitize option requires either --directory=some/path/here/ or 
      --file=file.txt to be set """
      sys.exit(1)

    for entry in sanitize_entries(entries, args.user, args.pwd, args.dbname, args.host, args.tlayout):
      print entry

  elif args.updateurl:
    pass
  else:
    print "Only --sanitize and --updateurl are valid modes of operation"
    sys.exit(1)

if __name__ == '__main__':
  main()
