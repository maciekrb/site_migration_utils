import logging
import os
from sitetools.utils import SEPARATOR
from sitetools.utils import convert_to_utf8

class PathCardinalityException(Exception):
  pass

class ShellScriptUtil:
  """
    { "sOme Path" : "somepath"
  """

  def __init__(self):
    self.flushed_paths = []
    self.directory_map = {}

  def get_move_statements(self, original, sanitized):

    """ Nothing to do if paths are equal """
    if original == sanitized: return None


    orig_base, orig_file = os.path.split(original)
    sntz_base, sntz_file = os.path.split(sanitized)
    orig_parts = orig_base.split(SEPARATOR)
    sntz_parts = sntz_base.split(SEPARATOR)

    self._map_paths(orig_parts, sntz_parts)
    base = self._resolve_path(orig_parts)
    logging.debug(" +==RBASE=> %s" % base)
    
    stack = []
    for part in self._resolve_tree_items(orig_parts):
      if len(part) > 1:
        partc = list(part)
        target = partc.pop()
        res_base = self._resolve_path(partc)
        full_base = res_base + SEPARATOR + target 
      else:
        full_base = part[0]

      stack.append(self._get_move_cmd(full_base, self._resolve_path(part)))

    stack.append(self._get_move_cmd(sntz_base + SEPARATOR + convert_to_utf8(orig_file), sanitized))
    return "\n".join(stack)
      

  def _map_paths(self, orig_parts, sntz_parts):
    logging.debug(" +==FRM=> %s" % orig_parts)
    logging.debug(" +==TO=> %s" % sntz_parts)

    if len(orig_parts) != len(sntz_parts):
      raise PathCardinalityException("Number of items in paths %s, %s does not match" % 
          (orig_parts, sntz_parts))

    for idx, val in enumerate(orig_parts):
      if val not in self.directory_map:
        self.directory_map[val] = sntz_parts[idx]

    logging.debug(" +==MAP=> %s" % self.directory_map)

  def _resolve_path(self, parts):
    sanitized_parts = []
    for p in parts:
      sanitized_parts.append(self.directory_map[p])

    return SEPARATOR.join(sanitized_parts)

  def _resolve_tree_items(self, path_parts):

    flushable = []
    if path_parts in self.flushed_paths:
      return flushable

    stack = []
    if path_parts[0] == '':
      stack.append(path_parts.pop(0))

    for p in path_parts:
      stack.append(p)
      if stack not in self.flushed_paths:
        flushable.append(list(stack))
        self.flushed_paths.append(list(stack))

    return flushable

  def _get_move_cmd(self, source, target):
    return u'mv "%s" %s' % (source, target)


