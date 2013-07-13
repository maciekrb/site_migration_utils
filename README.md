Site Migration Utilities
========================

Site Migration Utilities are a set of simple tools to assist in the migration process of CMS based sites. It's primary aim is to work as a simple command line tool that generates scripts (SQL and shell) that can perform changes in specific columns in a database, or rename paths / files in a file system.

```sh
$siteutil.py -h

usage: siteutil.py [-h] [--sanitize] [--replace] [-d DIRECTORY] [-f FILE]
                   [--filesystem] [--database] [--host HOST] [-u USER]
                   [-p PWD] [-n DBNAME] [-t TLAYOUT] [--needle NEEDLE]
                   [--replacement REPLACEMENT] [-v {WARN,INFO,DEBUG}]

Command line utils for website migration

optional arguments:
  -h, --help            show this help message and exit
  --sanitize            Sanitize mode, will search for ugly paths in the given
                        folder and try to nice them out.
  --replace             Update URL mode, will generate scripts to update from
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
  --needle NEEDLE       The value that will be searched for, and replaced
  --replacement REPLACEMENT
                        The value that will replace --needle
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

To sort the whole thing out, the actual paths need to be renamed in the file system, and thus
```sh
$siteutil.py --sanitize -d path/with/ugly/files --filesystem
```
generates something like this :

```sh
mv "path/with/ugly/files/uGlY fiLe.GIF" path/with/ugly/files/ugly-file.gif
mv "path/with/ugly/files/OTHER !nice! file.GIF" path/with/ugly/files/other-nice-file.gif
mv "path/with/ugly/files/Ugl Y Dir" path/with/ugly/files/uglydir
mv "path/with/ugly/files/uglydir/uGlY fiLe.GIF" path/with/ugly/files/uglydir/ugly-file.gif
```

Finally, when for example moving a very old Joomla site images to Amazon S3, you might want to do:

```sh
$siteutil.py --replace --needle=http://example.com/images \
  --replacement=http://example.com.s3.amazonaws.com/images --database \
  -u dbuser -p dbpass -n dbname -t jos_content:id:urlimage,fulltext
```

This would output : 
```sql
UPDATE `jos_content` SET 
 `urlimage` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 ) 
 `fulltext` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 ) WHERE `id` = '4297';
UPDATE `jos_content` SET 
 `urlimage` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 )
 `fulltext` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 ) WHERE `id` = '4368';
UPDATE `jos_content` SET 
 `urlimage` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 ) WHERE `id` = '4429';
UPDATE `jos_content` SET 
 `urlimage` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 ) WHERE `id` = '4506';
UPDATE `jos_content` SET 
 `urlimage` = REPLACE(path_imagen, 
  'http://example.com/images', 
  'http://example.com.s3.amazonaws.com/images'
 ) WHERE `id` = '5423';

```

Installation
============

Easiest way of getting up and running is using pip: `pip install git+https://github.com/maciekrb/site_migration_utils.git`. 

You will need to install the following dependencies:
  - `pip install mysql-python`
  - `pip install chardet`
  - `pip install git+https://github.com/maciekrb/py-textutils.git`

Bugs
====

Please feel free to report any unexpected behaviors or perks you might consider useful by using the issue tracker.
