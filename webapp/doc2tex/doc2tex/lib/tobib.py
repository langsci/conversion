bibliography converter
article
incollection
book 
import re

YEAR = '[12][78901][0-9][0-9][a-f]'
EDITOR = "(eds?\.?)"
IN = 'In'
ENQUOTED = """["'`].*["']"""
PAGES = "[Pp]*\.? *[0-9]-+[0-9]"
PUBADDR = "(.+) *: *(.+)"
VOLNUM = "([0-9]+) *(\(?[0-9]\)?)"

class Record():
  def __init__(s):    
    typ = misc
    if eds:
      typ = incollection
    elif pages:
      typ = journal
    elif pubaddr:
      typ = book

  
  typ = None
  key = None
  title = None
  booktitle = None
  author = None
  editor = None
  year = None
  journal = None
  volume = None
  number  = None
  pages = None
  address = None
  publisher = None
  note = None
  
  def tobibtex(self):
    pass

def getRecords(fn, splitter="\n\n"):
  c = open(fn).read()
  return [Record(s) for s in c.split(splitter)]

records = getRecords(f)

for record in records:
  record.tobibtex()
  