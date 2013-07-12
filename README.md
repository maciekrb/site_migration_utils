Site Migration Utilities
========================

Site Migration Utilities are a set of simple tools to assist in the migration process of CMS based sites. It's primary aim is to work as a simple command line tool that generates scripts (SQL and shell) that can perform changes in specific columns in a database, or rename paths / files in a file system.

```sh
$siteutil.py -h
usage: siteutil.py [-h] [--sanitize] [--updateurl] [-d DIRECTORY] [-f FILE]
                   [--filesystem] [--database] [--host HOST] [-u USER]
                   [-p PWD] [-n DBNAME] [-t TLAYOUT] [-v {WARN,INFO,DEBUG}]

Command line utils for website migration

optional arguments:
  -h, --help            show this help message and exit
  --sanitize            Sanitize mode, will search for ugly paths in the given
                        folder and try to nice them out.
  --updateurl           Update URL mode, will generate scripts to update from
                        a source url to a target url.
  -d DIRECTORY, --directory DIRECTORY
                        Base directory to search for ugly files
  -f FILE, --file FILE  Reads file paths from file, one per line
  --filesystem          Generates shell scripts to move paths
  --database            Generates SQL scripts to update DB
  --host HOST           Database host to connect
  -u USER, --user USER  Database user
  -p PWD, --pwd PWD     Database password
  -n DBNAME, --dbname DBNAME
                        Database name
  -t TLAYOUT, --tlayout TLAYOUT
                        Table layout as follows: table_name:id:co1,col2,col3
                        where id is a row unique id and col1, col2 and col3
                        are the columns in which the expression will be
                        searched
  -v {WARN,INFO,DEBUG}, --verbosity {WARN,INFO,DEBUG}
                        Verbosity level
```

Usage examples
--------------
Let's say you need to find all files that have ugly urls under a directory, and then check which records in a database actually reference those files:
```sh
$siteutil.py --sanitize -d path/with/ugly/files --database -u dbuser -p dbpass -n dbname \
             -t table1:id_col:search_col1,search_col2
```

The above line will traverse the ``path/with/ugly/files`` searching for ugly named files, and will then connect to the database specified by the given params in order to find every file path pattern in the search_col1 and search_col2 of table1. The actual output of the script is the following:
```sql

UPDATE `table1` SET
  `search_col1` = REPLACE(search_col1, 
    'path/with/ugly/files/uGlY fiLe.GIF',
    'path/with/ugly/files/ugly-file.gif'
  ) WHERE `id_col` = '34';

UPDATE `table1` SET
  `search_col1` = REPLACE(search_col1, 
    'path/with/ugly/files/OTHER !nice! file.GIF',
    'path/with/ugly/files/other-nice-file.gif'
  ),
  `search_col2` = REPLACE(search_col1, 
    'path/with/ugly/files/OTHER !nice! file.GIF',
    'path/with/ugly/files/other-nice-file.gif'
  ) WHERE `id_col` = '38';
```

Notice that only the columns that actually matched the file pattern inside of the content will attempt to be updated.

... more doc comming soon ...
