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

... more doc comming soon ...
