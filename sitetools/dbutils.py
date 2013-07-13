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

import logging
import MySQLdb
from sitetools.utils import convert_to_utf8

class DBExpressionFinder:

  skel = [ "SELECT {fields} from {table} WHERE {where}", "`{field}` like {pattern}"]

  def __init__(self, dbuser, dbpass, dbname, host='localhost', wildcard_start=True):
    db = MySQLdb.connect(host="localhost", user=dbuser, passwd=dbpass, db=dbname, charset='utf8') 
    self.cursor = db.cursor()
    self.table_map = {}
    self.sentence = {}
    self.wildcard = "%{}" if wildcard_start else "{}%"

  
  def register_target(self, table_name, search_columns, id_column):
    self.table_map[table_name] = { "columns": search_columns, "id_column": id_column } 

  def _get_sql_sentence(self, table, columns, id_column):
    where = []
    for col in columns:
      where.append(self.skel[1].format(field=col, pattern="%s"))

    return self.skel[0].format(
      fields=",".join(["`{}`".format(c) for c in columns + [ id_column ]]), 
      table=table, 
      where=" OR ".join(where)
    )

  def _get_matching_columns(self, table, needle, row):
    table = self.table_map[table]
    utf_needle = convert_to_utf8(needle)
    cols = []
    for key, val in row.iteritems():
      if key != table['id_column'] and isinstance(val, basestring):
        if val.find(utf_needle) > -1:
          cols.append(key)

    logging.debug("Columns matching needle: %s" % ",".join(cols))
    return cols

  def _make_update_statement(self, needle, replacement, table, cols, id_col, record_id):
    needle = needle.replace("'","\'")
    utf8_needle = convert_to_utf8(needle)
    rpl_col = u" `%s` = REPLACE(%s, \n  '%s', \n  '%s'\n )"
    stmt = u"UPDATE `{table}` SET \n".format(table=table)
    stmt += u",\n ".join([ rpl_col % (c, c, utf8_needle, replacement)  for c in cols ])
    stmt += u" WHERE `{id_col}` = '{record_id}';".format(id_col=id_col, record_id=record_id)
    logging.debug("<===== SQL UPDATE sentence ===>")
    logging.debug("%s" % stmt)
    logging.debug("<===== SQL UPDATE sentence ===>")
    return stmt.encode('utf8')


  def find_matches(self, needle, table):

    tbl = self.table_map[table]
    if table not in self.sentence:
      self.sentence[table] = self._get_sql_sentence(
        table, tbl['columns'], tbl['id_column']
      ).format(pattern=needle)
      logging.debug("<===== SQL sentence ===>")
      logging.debug(self.sentence[table]) 
      logging.debug("<===== SQL sentence ===>")

    sentence = self.sentence[table]

    logging.debug(" +=exec=> {}".format(sentence))
    self.cursor.execute(sentence, tuple([ self.wildcard.format(needle) for i in enumerate(tbl['columns'])]))
    columns = tuple( [d[0].decode('utf8') for d in self.cursor.description] )
    results = []
    for row in self.cursor.fetchall():
      results.append(dict(zip(columns, row)))
    return results

  def get_update_statements(self, needle, replacement):
    statements = []
    for table, data in self.table_map.iteritems():
      for row in self.find_matches(needle, table):
        cols = self._get_matching_columns(table, needle, row)
        if cols:
          upd = self._make_update_statement(
            needle, 
            replacement, 
            table, 
            cols, 
            data['id_column'], 
            row[data['id_column']]
          )
          statements.append(upd)
    
    return "\n".join(statements) if statements else None


  def replace_matches(self, needle, replacement):
    matches = self.find_matches(needle)
    utf_needle = convert_to_utf8(needle)
    for row in matches:
      logging.warn(" ---DB MATCH------------------------------>")
      logging.warn(" ---> %s" % utf_needle)
      logging.warn(" ---> %s" % replacement)
      for col in row:
        if isinstance(col, long):
          logging.warn("[ ID: %s] " % col)
        if isinstance(col, basestring):
          if col.find(utf_needle) > -1:
            x = col.replace(utf_needle, replacement)
            logging.warn(" <--------------------------FIELD STARTS ---------------------------------> ")
            logging.warn("%s" % x)
            logging.warn(" <--------------------------FIELD ENDS -----------------------------------> ")
