# --* encoding=utf8 *-- 
import sys
import re
import pprint 
 
#pattern definitions
year = '\(? *(?P<year>[12][78901][0-9][0-9][a-f]?) *\)?' 
pages = "(?P<pages>[0-9]+[-–]+[0-9]+)"
pppages = "\(?[Pps\. ]*%s\)?"%pages
author = "(?P<author>.*?)" #do not slurp the year
ed = "(?P<ed>\([Ee]ds?\.?\))?"
editor = "(?P<editor>.+)"
booktitle = "(?P<booktitle>.+)"
title = "(?P<title>.*)"
journal = "(?P<journal>.*?)"
numbervolume = "(?P<number>[-\.0-9/]+) *(\((?P<volume>[-0-9/]+)\))?"
pubaddr = "(?P<address>.+) *:(?!/) *(?P<publisher>[^:]+?)\.?"

#compiled regexes
BOOK = re.compile("{author} {ed}[., ]*{year}[., ]*{title}\. +{pubaddr}".format(author=author,
                                                                          ed=ed,
                                                                          year=year,
                                                                          title=title,
                                                                          pubaddr=pubaddr))
ARTICLE = re.compile("{author}[., ]*{year}[., ]*{title}\. +{journal},? *{numbervolume}[\.,] *{pages}"\
            .format(pages=pppages,
                    author=author,
                    year=year,
                    journal=journal,
                    numbervolume=numbervolume,
                    title=title)
                    )
INCOLLECTION = re.compile("{author}[., ]*{year}[., ]*{title}\. In {editor} \([Ee]ds?\. *\), {booktitle}[\.,]? {pages}\. +{pubaddr}\."\
                      .format(author=author,
                              year=year,
                              title=title,
                              editor=editor,
                              booktitle=booktitle,
                              pages=pppages,
                              pubaddr=pubaddr)
                              )
MISC = re.compile("{author}[., ]*{year}[., ]*{title}\.? *(?P<note>.*)".format(author=author, year=year, title=title))

#regexes for telling entry types    
EDITOR = re.compile("[0-9]{4}.*(\([Ee]ds?\.?\))") #make sure the editor of @incollection is only matched after the year
PAGES = re.compile(pages)
PUBADDR = re.compile(pubaddr)

#fields to output
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
    "note",
    "url"
    ]
    
    
class Record():
  def __init__(self,s):    
    self.orig = s    
    self.bibstring = s
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
    self.url = None 
    if  EDITOR.search(s):
      self.typ = "incollection"
      m = INCOLLECTION.search(s) 
      #print 1
      if m: 
        #print 2
        self.author = m.group('author')
        self.editor = m.group('editor')
        self.title = m.group('title')
        self.booktitle = m.group('booktitle')
        self.year = m.group('year') 
        self.address = m.group('address')
        self.publisher = m.group('publisher')
        self.pages = m.group('pages') 
        #pprint.pprint(self.__dict__)
    elif  PAGES.search(s):      
      self.typ = "article"
      m = ARTICLE.search(s)
      if m:
        self.author = m.group('author')
        self.title = m.group('title')
        self.year = m.group('year')
        self.journal = m.group('journal')
        self.number = m.group('number')
        self.volume = m.group('volume')
        self.pages = m.group('pages')   
    elif PUBADDR.search(s):
      self.typ = "book"  
      m = BOOK.search(s) 
      if m:
        self.author = m.group('author')
        if m.group('ed') != None:
          self.editor = m.group('author')
          self.author = None
        self.title = m.group('title')
        self.year = m.group('year')
        self.address = m.group('address')
        self.publisher = m.group('publisher')
    else: 
      m = MISC.search(s)
      if m:
        self.author = m.group('author')
        self.title = m.group('title')
        self.year = m.group('year')
        self.note = m.group('note') 
    #print self.editor
    try:
      self.author = self.author.replace('&', ' and ')
    except AttributeError: 
      try:
        self.editor = self.editor.replace('&', ' and ')
      except AttributeError:
        return
    if self.title and "http" in self.title:
      print 2
      t = self.title.split("http:")[0]
      self.url="http:"+'http://zxZC'.join(self.title.split("http:")[1:])
      self.title=t
    #http
    #series volume
    authorpart = "Anonymous"
    yearpart = "9999" 
    try: 
      authorpart = self.author.split(',')[0].split(' ')[0] 
    except AttributeError: 
      authorpart = self.editor.split(',')[0].split(' ')[0] 
    try:
      yearpart = self.year[:4]
    except TypeError:
      return
    key = authorpart+yearpart 
    bibstring="@%s{%s,\n\t"%(self.typ,key)    
    fields = [(f,self.__dict__[f]) for f in self.__dict__ if f in FIELDS and self.__dict__[f]!=None]
    fields.sort()
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
  