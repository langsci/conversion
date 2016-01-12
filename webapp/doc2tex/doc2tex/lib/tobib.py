#bibliography converter
#article
#incollection
#book 
import sys
import re

YEAR = '[12][78901][0-9][0-9][a-f]'
EDITOR = re.compile("(eds?\.?)")
IN = 'In'
ENQUOTED = """["'`].*["']"""
PAGES = re.compile("[Pp]*\.? *[0-9][-–]+[0-9]")
PUBADDR = re.compile("(.+) *: *(.+)")
VOLNUM = "([0-9]+) *(\(?[0-9]\)?)"

class Record():
  def __init__(self,s):    
    self.typ = "misc"
    if  EDITOR.search(s):
      self.typ = "incollection"
    elif  PAGES.search(s):
      self.typ = "article"
    elif PUBADDR.search(s):
      self.typ = "book" 
    self.key = None
    self.title = None
    self.booktitle = None
    self.author = None
    self.editor = None
    self.year = None
    self.journal = None
    self.volume = None
    self.number  = None
    self.pages = None
    self.address = None
    self.publisher = None
    self.note = None
  
  def tobibtex(self):
    print(self.typ)

def getRecords(fn, splitter="\n\n"):
  c = open(fn).read()
  return [Record(s) for s in c.split(splitter)]

#records = getRecords(f)

#for record in records:
  #record.tobibtex()
  
if __name__=="__main__":
  fn = sys.argv[1]
  lines = open(fn).readlines()
  for l in lines:
    r = Record(l)
    r.tobibtex()