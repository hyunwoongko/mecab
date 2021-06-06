import os
from mecab.common import MECAB_DEFAULT_RC, DICRC
from mecab.common import CHECK_DIE
from mecab.utils.param import Param
from mecab.utils.string_utils import create_filename, remove_filename, replace_string

def load_dictionary_resource(param: Param):
  rcfile = param.get('rcfile')

  if not rcfile:
    homedir = os.getenv('HOME')
    if homedir:
      s = create_filename(homedir, '.mecabrc')
      ifs = open(str(s), "r")
      if ifs:
        rcfile = s 

  if not rcfile:
    rcenv = os.getenv('MECABRC')
    if rcenv:
      rcfile = rcenv 
  
  if not rcfile:
    rcfile = MECAB_DEFAULT_RC

  if param.parse_file(rcfile):
    return False
  
  dicdir = param.get('dicdir')
  if not dicdir:
    dicdir = '.' # current

  rcpath = remove_filename(rcfile)
  dicdir = replace_string(dicdir, '$(rcpath)', rcpath)
  param.set('dicdir', dicdir, True)
  dicrc = create_filename(dicdir, DICRC)

  return param.parse_file(dicrc)

def get_all_csvs_in_directory(path: str, dics:list(str)):
  dics.clear()
  filenames = os.listdir(path)
  for filename in filenames:
    if filename.endswith('.csv'):
      dics.append(filename)
