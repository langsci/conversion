import re
import glob
import sys

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
      for ap,msg in self.antipatterns:
	m = re.search('(%s)'%ap,l)
	if m != None:
	  g = m.group(1)
	  if g!='':
	    self.errors.append("%i: %s\n\t%s" % (i,g,msg))
	    
  def printErrors(self):
    print self.fn
    print '%i possible errors found' % len(self.errors)
    print '\n'.join(self.errors).encode('utf8')
  
  antipatterns = ()
	    

class TexFile(LSPFile):  
  antipatterns = (
    (r" et al.","Please use the citation commands \\citet and \\citep"),      #et al in main tex
    (r"setfont","You should not set fonts explicitely"),      #no font definitions
    #(r"\\ref","It is often advisable to use the more specialized commands \\tabref, \\figref, \\sectref, and \\REF for examples"),      #no \ref
    ("",""),      #\ea\label
    ("",""),      #\section\label
    ("",""),      #captions end with .
    ("",""),      #footnotes end with .
    (r"\[[0-9]+,[0-9]+\]","Please use a space after the comma in lists of numbers "),      #no 12,34 without spacing
    ("",""),      #(\citealt)
    ("",""),      #egrep cite[altp]+\{a-zA-Z0-9\}+\}, \\cite 
    (r"[0-9 ]ff","Do not use ff. Give full page ranges"),      #ff
    (r"[^-]---[^-]","Use -- with spaces rather than ---"),      #-- not ---
    (r"tabular.*\|","Vertical lines in tables should be avoided"),             #no | in tabular
    (r"\\hline","Use \\midrule rather than \\hline in tables"),                    #no hline
    (r"\\section.*[A-Z].*[A-Z].*","Only capitalize this if it is a proper noun"),                    #no special capitalization in sections
    #("",""),                    #gll ends with punctuation %difficult to asses whether full phrase of only NP or so
    #("","")                    #glt ends with punctuation                   
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
    ("[Aa]ddress *=.*[,/].*[^ ]","No more than one place of publication. No indications of countries or provinces"), #double cities in address
    ("[Aa]ddress *=.* and .*","No more than one place of publication."), #double cities in address
    ("[Tt]itle * =.*: +(?<!{)[a-zA-Z]+","Subtitles should be capitalized. In order to protect the capital letter, enclose it in braces {} "), #: [a-z] in bib
    ("[Aa]uthor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*","Full author names should be given. Only use abbreviated names if the author is known to prefer this. It is OK to use middle initials"), #full author names
    ("[Ee]ditor *=.*(?<=(and|AND|..[,{])) *[A-Z]\..*","Full editor names should be given. Only use abbreviated names if the editor is known to prefer this. It is OK to use middle initials"), #full author names
    ("[Aa]uthor *=.* et al","Do not use et al. in the bib file. Give a full list of authors"), #no et al in authors
    ("[Aa]uthor *=.*&.*","Use 'and' rather than & in the bib file"), #no et al in authors
    ("[Tt]itle *=(.* )?[IVXLCDM]+[\.,\) ]","In order to keep the Roman numbers in capitals, enclose them in braces {}"), #[IVXLCDM] no braces      
    )

#year not in order in multicite

if __name__ == "__main__":
  try:
    d = sys.argv[1]
  except IndexError:
    d = '.'
  texfiles = glob.glob('%s/*.tex'%d)
  bibfiles = glob.glob('%s/*.bib'%d)
  print "checking %s" % ' '.join([f for f in texfiles+bibfiles])
  for tfn in texfiles:
    t = TexFile(tfn)
    t.check()
    t.printErrors()
  for bfn in bibfiles:
    b = BibFile(bfn)
    b.check()
    b.printErrors()
  