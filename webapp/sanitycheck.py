import re
import glob
import sys

class LSPError:
  def __init__(self,fn,linenr,line,offendingstring,msg):
    self.fn = fn
    self.linenr = linenr
    self.line = line
    self.offendingstring = offendingstring
    self.msg = msg
    
  def __str__(self):
    print "{linenr}:{offendingstring}\n{msg}".format(self.__dict__).encode('utf8')

class LSPFile:
  def __init__(self,fn):
    self.fn = fn
    self.content = open(fn).read().decode('utf8')
    self.lines = self.split_(self.content)
    self.errors = []
    
  def split_(self,c):
    result = self._removecomments(c).split('\n')
    return result
    
  def _removecomments(self,s):
    #negative lookbehind 
    result = re.sub('(?<!\\\\)%.*\n','\n',s)
    return result
	    
  def check(self):
    self.errors=[]
    for i,l in enumerate(self.lines):
      if '\\chk' in l: #the line is explicitely marked as being correct
	continue
      for ap,msg in self.antipatterns:
	m = re.search('(%s)'%ap,l)
	if m != None:
	  g = m.group(1)
	  if g!='':	    
	    self.errors.append(LSPError(fn,i,l,g,msg)	    
      for posp,negp,msg in self.posnegpatterns:	
	posm = re.search('(%s)'%posp,l)
	if posm==None:
	  continue
	g = posm.group(1)
	negm = re.search(negp,l)
	if negm==None:
	  self.errors.append(LSPError(fn,i,l,g,msg)	
	  
	  
	
  antipatterns = ()
  posnegpatterns = () #if first part, then second part, otherwise error

class TexFile(LSPFile):  
  antipatterns = (
    (r" et al.","Please use the citation commands \\citet and \\citep"),      #et al in main tex
    (r"setfont","You should not set fonts explicitely"),      #no font definitions
    #(r"\\ref","It is often advisable to use the more specialized commands \\tabref, \\figref, \\sectref, and \\REF for examples"),      #no \ref
    #("",""),      #\ea\label
    #("",""),      #\section\label
    ("\\caption\{.*[^\.]\} +$","The last character of a caption should be a '.'"),      #captions end with .
    #("",""),      #footnotes end with .
    (r"\[[0-9]+,[0-9]+\]","Please use a space after the comma in lists of numbers "),      #no 12,34 without spacing
    ("\([^)]+\\cite[pt][^)]+\)","In order to avoid double parentheses, it can be a good idea to use \\citealt instead of \\citet or \\citep"),    
    ("([0-9]+-[0-9]+)","Please use -- for ranges instead of -"),      
    (r"[0-9]+ *ff","Do not use ff. Give full page ranges"),
    (r"[^-]---[^-]","Use -- with spaces rather than ---"), 
    (r"tabular.*\|","Vertical lines in tables should be avoided"),   
    (r"\hline","Use \\midrule rather than \\hline in tables"),      
    (r"\gl[lt] *[a-z].*[\.?!] *\\\\ *$","Complete sentences should be capitalized in examples"), 
    (r"\section.*[A-Z].*[A-Z].*","Only capitalize this if it is a proper noun"), 
    (r"\section.*[A-Z].*[A-Z].*","Only capitalize this if it is a proper noun"), 
    (r"[A-Z]{3,}","It is often a good idea to use \\textsc\{smallcaps\} instead of ALLCAPS"),                   
      )

  posnegpatterns = (
    (r"\[sub]*section\{",r"\label","All sections should have a \\label. This is not necessary for subexamples."),
    (r"\ea.*",r"\label","All examples should have a \\label"),
    (r"\gll.*[A-Z]",r"[\.?!] *\\\\ *$","All vernacular sentences should end with punctuation"),
    (r"\glt.*[A-Z]",r"[\.?!]' *$","All translated sentences should end with punctuation"),
    )
    
  filechecks = (
    ("",""),    #src matches #imt
    ("",""),     #words
    ("",""),     #hyphens
    ("",""),    #tabulars have lsptoprule
    ("",""),    #US/UK                    
    )
   


class BibFile(LSPFile):
  
  antipatterns = (
    #("[Aa]ddress *=.*[,/].*[^ ]","No more than one place of publication. No indications of countries or provinces"), #double cities in address
    #("[Aa]ddress *=.* and .*","No more than one place of publication."), #double cities in address
    ("[Tt]itle * =.*: +(?<!{)[a-zA-Z]+","Subtitles should be capitalized. In order to protect the capital letter, enclose it in braces {} "), 
    ("[Aa]uthor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*","Full author names should be given. Only use abbreviated names if the author is known to prefer this. It is OK to use middle initials"),
    ("[Ee]ditor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*","Full editor names should be given. Only use abbreviated names if the editor is known to prefer this. It is OK to use middle initials"),
    ("[Aa]uthor *=.* et al","Do not use et al. in the bib file. Give a full list of authors"), 
    ("[Aa]uthor *=.*&.*","Use 'and' rather than & in the bib file"), 
    ("[Tt]itle *=(.* )?[IVXLCDM]*[IVX]+[IVXLCDM]*[\.,\) ]","In order to keep the Roman numbers in capitals, enclose them in braces {}"), 
    )

#year not in order in multicite


class LSPDir:
  def __init__(self,dirname):
    self.dirname = dirname
    self.texfiles = glob.glob('%s/*.tex'%dirname)
    self.bibfiles = glob.glob('%s/*.bib'%dirname)
    self.errors={}
  	    
  def printErrors(self):
    for fn in self.errors:
      print fn
      fileerrors = self.errors[fn]
      print '%i possible errors found' % len(fileerrors)
      for e in fileerrors:
	print e
  
  def check(self):
    for tfn in self.texfiles:
      t = TexFile(tfn)
      t.check()
      self.errors[tfn] = t.errors
    for bfn in self.bibfiles:
      b = BibFile(bfn)
      b.check()
      self.errors[bfn] = b.errors
    
 
    
if __name__ == "__main__":
  try:
    d = sys.argv[1]
  except IndexError:
    d = '.'
  lspdir = LSPDir(d)
  print "checking %s" % ' '.join([f for f in lspdir.texfiles+lspdir.bibfiles])
  lspdir.check()
  lspdir.printErrors()