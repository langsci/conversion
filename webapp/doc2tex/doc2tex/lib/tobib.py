# --* encoding=utf8 *--
#bibliography converter
#article
#incollection
#book 
import sys
import re
import pprint 

YEAR = '[12][78901][0-9][0-9][a-f]'
EDITOR = re.compile("(\(eds?\.?\))")
IN = 'In'
ENQUOTED = """["'`].*["']"""
PAGES = re.compile("[Pp]*\.? *[0-9][-–]+[0-9]")
PUBADDR = re.compile("(.+) *: *(.+)")
VOLNUM = "([0-9]+) *(\(?[0-9]\)?)"
BOOK = re.compile("(?P<author>.*?)[., ]*\(?(?P<year>[12][78901][0-9][0-9][a-f]?)\)?[., ]*(?P<title>.*)\. +(?P<address>.+) *: *(?P<publisher>.*?)\.")
ARTICLE = re.compile("(?P<author>.*?)[., ]*\(?(?P<year>[12][78901][0-9][0-9][a-f]?)\)?[., ]*(?P<title>.*)\. +(?P<journal>.*) (?P<number>[-0-9]+)\. (?P<pages>[-–0-9]+)")
INCOLLECTION = re.compile("(?P<author>.*?)[., ]*\(?(?P<year>[12][78901][0-9][0-9][a-f]?)\)?[., ]*(?P<title>.*)\. In (?P<editor>.*) \(eds?\.\), (?P<booktitle>.*), (?P<pages>[-–0-9]+). (?P<address>.+) *: *(?P<publisher>.+)\.")

FIELDS = ["key",
    "title",
    "booktitle",
    "author",
    "editor",
    "year",
    "journal",
    "volume",
    "number",
    "pages",
    "address",
    "publisher",
    ]
    
class Record():
  def __init__(self,s):    
    self.orig = s
    self.typ = "misc"    
    self.key = None
    self.title = None
    self.booktitle = None
    self.author = "Anonymous"
    self.editor = None
    self.year = None
    self.journal = None
    self.volume = None
    self.number  = None
    self.pages = None
    self.address = None
    self.publisher = None
    self.note = None 
    if  EDITOR.search(s):
      self.typ = "incollection"
      m = INCOLLECTION.search(s)
      if m:
        self.author = m.group('author')
        self.editor = m.group('editor')
        self.title = m.group('title')
        self.booktitle = m.group('booktitle')
        self.year = m.group('year') 
        self.address = m.group('address')
        self.publisher = m.group('publisher')
        self.pages = m.group('pages') 
    elif  PAGES.search(s):      
      self.typ = "article"
      m = ARTICLE.search(s)
      if m:
        self.author = m.group('author')
        self.title = m.group('title')
        self.year = m.group('year')
        self.journal = m.group('journal')
        self.number = m.group('number')
        self.pages = m.group('pages')   
    elif PUBADDR.search(s):
      self.typ = "book"  
      m = BOOK.search(s)
      if m:
        self.author = m.group('author')
        self.title = m.group('title')
        self.year = m.group('year')
        self.address = m.group('address')
        self.publisher = m.group('publisher')
    else:
      self.parsemisc(s) 
    #self.bibstring = self.tobibtex()   
    try:
      self.author = self.author.replace('&', ' and ')
    except AttributeError:
      pass 
    try:
      self.editor = self.editor.replace('&', ' and ')
    except AttributeError:
      pass
    authorpart = "Anonymous"
    yearpart = "9999" 
    try: 
      authorpart = self.author.split(',')[0].split(' ')[0] 
    except AttributeError: 
      authorpart = self.editor.split(',')[0].split(' ')[0] 
    try:
      yearpart = self.year[:4]
    except TypeError:
      pass
    key = authorpart+yearpart 
    bibstring="@%s{%s,\n\t"%(self.typ,key)    
    fields = [(f,self.__dict__[f]) for f in self.__dict__ if f in FIELDS and self.__dict__[f]!=None]
    bibstring+=",\n\t".join(["%s = {%s}"%f for f in fields])
    bibstring+="\n}"  
    #print bibstring
    self.bibstring = bibstring
    
     


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
    if l.strip=='':
      continue
    r = Record(l) 
    print r.bibstring
    #r.tobibtex()
  