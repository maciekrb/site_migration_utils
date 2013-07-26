import platform

SEPARATOR = '\\' if platform.system().startswith('Win') else '/'

import logging
from chardet import detect
from textutils import sanitize

def convert_to_utf8(text):
  try:
    text = text.decode('utf8')
  except UnicodeEncodeError:
    charset = detect(text)
    logging.debug('Chardet[{text}] {encoding}, conf:{confidence}'.format(text=text, **charset))
    text = text.decode(charset['encoding'], 'ignore')
    text = text.encode('utf8', 'ignore')
  return text

def batch_replace(text, needle=['_'], replacement=['-']):
  for k,v in enumerate(needle):
    text = text.replace(v, replacement[k])
  return text

def sanitize_path(path):
  #path = batch_replace(path)
  parts = []
  for part in path.split(SEPARATOR):
    try:
      fname, ext = part.rsplit('.', 1)
      logging.debug("POINT SPLIT %s.%s" % (fname, ext))
      parts.append("{0}.{1}".format(sanitize(fname.strip(), allow_spaces=False, remap_unicode=True), ext))
    except ValueError:
      parts.append(sanitize(part, allow_spaces=False, remap_unicode=True))
      
  return SEPARATOR.join(parts).lower()
