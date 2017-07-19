# -*- coding: utf-8 -*-

import sys
import xml.etree.ElementTree as etree
import re

CONSONANTS = 'bcdfghjkḱlĺmḿńǹŋpṕrŕsśtvwzʒ'
ONSET = 'bcdfghjkḱlĺmḿńǹnŋpṕrŕsśtvwzʒGKŊʧʤ'
CODAS = 'mnŋgklr'
VOWELS = 'aAáÁàâãāãȁeéèẽēȅɛəiíìĩīȉɪoóòõṍȭōȍɔuúùũṹūȕʊnʊʊ́ɔɛɪ́ɪ̄ɛ̄ɪ́'#n
SECONDGLYPHS = "mpbʃʒ $"
currentletter = 'x'

def hyphenate(s):
    #p = "(?<=[%s])([%s])(?![%s])"%(VOWELS,CONSONANTS,SECONDGLYPHS)
    #temporarily get rid off digraphs  
    mod = s
    p = "([%s][%s]?)([%s][^%s ]?)([%s])"%(VOWELS,CODAS,ONSET,VOWELS,VOWELS)
    mod = re.sub(p,r"\1\\-\2\3",mod)   
    return mod
    

def normalize(s):
      replacements = [('ᵃ','{\higha}'),
                      ('ᵉ','{\highe}'),
                      ('ᵋ','{\highE}'),
                      ('ᶦ','{\highI}'),
                      ('ᵒ','{\higho}'),
                      ('ᵓ','{\highO}'),
                      ('ᵘ','{\highu}'),
                      ('ᶷ','{\highU}')
                      ]
      for r in replacements:
        s = s.replace(r[0],r[1])
      return s
  
def cmd(command, value, indent=0):
    try:
        value = normalize(value)
        value = value.replace("#","\#")\
          .replace("&","\&")\
          .replace("_","\_")\
          .replace("ɪ","ɨ")\
          .replace("ʊ","ʉ")\
          .replace("Ʊ","Ʉ")
    except AttributeError:
        pass
    return 0*' '+"\\%s{%s}%%"%(command, value) 

def hypercmd(command, anchor, value, indent=0):
  #value = value.replace("#","\#").replace("&","\&").replace("_","\_")
    value = normalize(value)
    return 0*' '+"\\hypertarget{%s}{}%%\n%s"%(anchor,cmd(command,value)) 
 
def fromtext(e, label):  
  try: 
    return e.find('.//%s'%label).text
  except AttributeError:
    return None
    
 
def fromformtext(e,label):
  return fromtext(e, "%s/form/text"%label)
  
def fromfieldformtext(e,field):
  return fromformtext(e,"field[@type='%s']"%field) 
    
    
    
def fromtagformtext(e,field):
  return fromformtext(e,"tag[@type='%s']"%field) 
      
      
def fromnoteformtext(e,field):
  return fromformtext(e,"note[@type='%s']"%field) 
  
def printsafe(e, field):
  value =  e.__dict__.get(field, False)
  if value:
    print(cmd(field, value))
 
class LexEntry():
    
    def __init__(self,e):
        def normalizeword(s): 
          if s == None:
            return ''
          replacements = [("aAáÁàÀâ","a"),
              ("bB","b"),
              ("ɓƁ","ɓ"),
              ("cC","c"),
              ("dD","d"),
              ("ɗƊ","ɗ"),
              ("eEéèê","e"),
              ("ɛƐɛ́ɛ̀","ɛ"),
              ("fF","f"),
              ("gGɡ","g"),
              ("h","h"),
              ("ɦ","ɦ"), 
              ("iIíÍìÌîɪⁱ","i"),
              ("jJ","j"),
              ("kK","k"),
              ("ƙƘ","ƙ"),
              ("lL","l"),
              ("mMḿ","m"),
              ("nNńǹ","n"),
              ("Ɲɲ","ɲ"),
              ("ŋŊ","ŋ"),
              ("oOóÓòÒô","o"),
              ("ɔƆɔ̂","ɔ"),
              ("pP","p"),
              ("rR","r"),
              ("sS","s"),
              ("tT","t"),
              ("uUúÚùû","u"),
              ("Ʊ","ʊ"), 
              ("vV","v"),
              ("wW","w"),
              ("xX","x"),
              ("yY","y"),
              ("zZ","z"),
              ("ʒƷ","ʒ")]
          for r in replacements:
            oldletters = r[0]
            newletter = r[1]
            for ol in oldletters:
              s = s.replace(ol,newletter)
          s = s.replace('ts','ʦ')
          s = s.replace('dz','ǳ')
          return s
          
        def keyIk(s):
          alphabet = " aᵃbɓcdɗǳeᵉɛᵋfɡghɦiɨᶦjʝkƙlmnɲŋoᵒɔᵓprstʦuᵘʊᶷʉvwxyzʒʼ."   
          try:                                                    
            result =  tuple([alphabet.index(ch) for ch in s])     
          except ValueError:                                      
            print(s)                                              
            0/0                                                  
          return result
            
          
        global currentletter
        self.ID = e.attrib.get('id', False)
        self.citationform = fromformtext(e,"citation")
        self.collationform = normalizeword(self.citationform)
        self.collationkey = keyIk(self.collationform)
         
        self.morphtype = e.find("trait[@name='morph-type']").attrib["value"]
        if self.morphtype != 'phrase':  
            self.lexicalunit = fromformtext(e,"lexical-unit")
        self.headword = Headword(self.citationform)   
        if self.citationform == None:
          self.headword = Headword(self.lexicalunit)    
        self.normalizedstartletter = normalizeword(self.headword.word.replace("=",'')[0])   
        try:
          self.note = e.find("note/form/text").text         #FIXME no semantics
        except AttributeError:
          pass   
        self.literalmeaning = fromfieldformtext(e,'literal-meaning')   
        self.root = fromfieldformtext(e,'Root') 
        self.plural = fromfieldformtext(e,'Plural') 
        try:
          self.plural = hyphenate(self.plural)  
        except TypeError:
          pass  
        self.senses =  [Sense(s) for s in e.findall('sense')]
    
    def toLatex(self):          
        self.headword.toLatex() 
        printsafe(self, 'citationform') #2 A
        printsafe(self, 'lexicalunit') #1 B
        printsafe(self, 'plural')  #5 D
        if len(self.senses)==1:
            self.senses[0].toLatex()
        else:
            for i,s in enumerate(self.senses):
                s.toLatex(number=i+1)
        printsafe(self, 'literalmeaning') #4 J
        printsafe(self, 'note') #3 J

class Headword():
    def __init__(self, s, firstwordofletter=False):
        #self.homograph = False
        self.firstwordofletter = firstwordofletter 
        self.word = s
        
    def toLatex(self):
        print("\\newentry")
        #print(cmd('headword',self.word))
        
class Pronunciation():
    def __init__(self,p): 
        self.ipa = p.find('.//Run').text 
        self.anchor = p.attrib.get('id',False)
        
    def toLatex(self): 
        latexipa = self.ipa.replace('ꜜ','{\downstep}')
        if self.anchor:
            print(hypercmd('ipa',self.anchor, latexipa, indent=1))
        else:
            print(cmd('ipa', latexipa, indent=1))
    
class Sense():
    def __init__(self,s):
        self.anchor = s.attrib.get('id',False)        
        tmppos = s.find(".//grammatical-info").attrib['value']        
        posd = {
          "Adverb":"adv",
          "Complementizer":"comp",
          "Coordinating connective":"coordconn",
          "Demonstrative":"dem",
          "Ideophone":"ideo",
          "Interjection":"interj",
          "Noun":"n",
          "Numeral":"num",
          "Nursery word":"nurs",
          "Preposition":"prep",
          "Pronoun":"pro",
          "Quantifier":"quant",
          "Relativizer":"rel",
          "Subordinating connective":"subordconn",
          "Verb":"v",
        }
        self.pos = posd[tmppos.strip()]        
        self.glosses = fromtext(s,"gloss/text")
        self.definition = fromformtext(s,"definition")
        self.scientificname = fromfieldformtext(s,'scientific-name')        
        self.sematicnote = fromnoteformtext(s,'semantics')
        
    
    def toLatex(self,number=False):
        if number:
          print(cmd('sensenr',number,indent=1))
        printsafe(self, 'pos') #8 C
        printsafe(self, 'scientificname') #9 D
        if self.__dict__.get('definition'):#7 E
            if self.anchor:
                print(hypercmd('definition',self.anchor,self.definition,indent=3))
            else:
              print(cmd('definition',self.definition,indent=3))
        printsafe(self, 'glosses') #6 0
        printsafe(self, 'semantics') #10 J
            


  
  
  
            
#===================



fn = sys.argv[1]
tree = etree.parse(fn)
root = tree.getroot()

lexentries = []

for entry in root.findall('.//entry'):
  lexentries.append(LexEntry(entry))
  
linkd = {}
for le in lexentries:
  ID = le.ID
  headword = le.headword.word
  linkd[le.ID] = headword
   
startletter = 'a'
print("\\end{letter}\n\\begin{letter}{a}""")
for le in sorted(lexentries, key=lambda l: l.collationkey):
  print("%"+30*"-")
  if le.normalizedstartletter != startletter: 
      print("\\end{letter}\n\\begin{letter}{%s}"""%(le.normalizedstartletter)) 
      startletter = le.normalizedstartletter
  le.toLatex()
print("\\end{letter}")
  