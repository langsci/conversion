# -*- coding: utf-8 -*-

import sys
import xml.etree.ElementTree as etree
import re

CONSONANTS = u'bcdfghjkḱlĺmḿńǹŋpṕrŕsśtvwzʒ'
ONSET = u'bcdfghjkḱlĺmḿńǹnŋpṕrŕsśtvwzʒGKŊʧʤ'
CODAS = u'mnŋgklr'
VOWELS = u'aAáÁàâãāãȁeéèẽēȅɛəiíìĩīȉɪoóòõṍȭōȍɔuúùũṹūȕʊnʊʊ́ɔɛɪ́ɪ̄ɛ̄ɪ́'#n
SECONDGLYPHS = u"mpbʃʒ $"
currentletter = 'x'

def hyphenate(s):
    #p = u"(?<=[%s])([%s])(?![%s])"%(VOWELS,CONSONANTS,SECONDGLYPHS)
    #temporarily get rid off digraphs
    subs = [(u'tʃ',u'ʧ'),
            (u'dʒ',u'ʤ'),
            (u'gb',u'GB'),
            (u'kp',u'KP'),
            (u'ŋm',u'ŊM')
            ]
    mod = s
    p = u"([%s][%s]?)([%s][^%s ]?)([%s])"%(VOWELS,CODAS,ONSET,VOWELS,VOWELS)
    for sub in subs:
      mod = mod.replace(sub[0],sub[1])
    mod = re.sub(p,r"\1\\-\2\3",mod)   
    #reinstate digraphs    
    for sub in subs:
      mod = mod.replace(sub[1],sub[0])
    return mod
  
def cmd(c,v, indent=0):
    return 0*u' '+u"\\%s{%s}%%"%(c,v) 

def hypercmd(command, anchor, value, indent=0):
    return 0*u' '+u"\\hypertarget{%s}{}%%\n%s"%(anchor,cmd(command,value)) 

def getText(e,field,strtype):
    try:
        runs = e.findall('%s/%s/Run'%(field,strtype))
        a = []
        for run in runs:
          if run.attrib.get('ws') == 'cli' or run.attrib.get('namedStyle') == 'Emphasized Text':
            a.append("\\textsl{%s}" % run.text)
          else:
            a.append(run.text)
        return ''.join(a)
    except AttributeError:
        return False
      
 
class LexEntry():
  
    def __init__(self,e):
        global currentletter
        t = e.find('_Self')
        if t != None:
          e=t
        self.ID = e.attrib.get('id', False)
        self.etymology = Etymology(e.find('.//LexEtymology'))
        self.headword = Headword(e.find('LexEntry_HeadWord'),anchor=self.ID)
        if self.headword.word.startswith(currentletter):
          self.firstwordofletter = False
        else:
          self.firstwordofletter = True
          currentletter = self.headword.word[0]
        self.literalmeaning = getText(e,'LexEntry_LiteralMeaning','AStr')
        try:
            self.pronunciations = [Pronunciation(p) for p in  e.find('LexEntry_Pronunciations').findall('LexPronunciation')]
        except AttributeError:
            #print("no pronunciation for {}".format(e.attrib["id"]))
            self.pronunciations = []
        self.mlr = MimimalLexReferences(e.find('_MinimalLexReferences'))
        self.vfebr = VariantFormEntryBackRefs(e.find('_VariantFormEntryBackRefs')) 
        self.vver = VisibleVariantEntryRef(e.find('_VisibleVariantEntryRefs')) 
        self.pos = getText(e,'MoStemMsa/MoStemMsa_MLPartOfSpeech','AStr')
        self.senses =  [Sense(s) for s in e.findall('LexEntry_Senses/LexSense')]
        self.plural = getText(e,'LexEntry_plural_form','Str') 
        if self.plural:
          self.plural = hyphenate(self.plural)
    
    def toLatex(self): 
     
        if self.firstwordofletter==True:
          try:
            print u"\\end{letter}\n\\begin{letter}{%s}"""%(self.headword.word[0].lower().encode('utf-8'),
                                                            #self.headword.word[0].lower().encode('utf-8')
                                                            )
          except UnicodeError:
            pass
        self.headword.toLatex()
        if len(self.pronunciations) == 0 and len(self.vver.lexentryreflinks)==0:
            print '{\\fixpron}','%%',self.vver.lexentryreflinks
        for p in self.pronunciations:
            p.toLatex()
        if self.pos:
            print cmd("pos", self.pos)
        if self.literalmeaning:
            print cmd('literalmeaning',self.literalmeaning)   
        if self.mlr:
            self.mlr.toLatex()
        if self.vfebr:
            self.vfebr.toLatex()
        if self.vver:
            self.vver.toLatex()                
        if len(self.senses)==1:
            self.senses[0].toLatex()
        else:
            for i,s in enumerate(self.senses):
                s.toLatex(number=i+1)
        self.etymology.toLatex()
        if self.plural:
            print cmd("plural", self.plural).encode('utf8')

class Headword():
    def __init__(self,e,anchor=False, firstwordofletter=False):
        self.anchor = anchor
        self.homograph = False
        self.firstwordofletter = firstwordofletter
        if e == None:
          self.word = r"\error{no headword!}"          
          return
        self.word = e.findall('.//Run')[0].text 
        try:
            self.homograph = e.findall('.//Run')[1].text #better use attrib named style
        except IndexError:
            pass
      
    def toLatex(self):
        print "\\newentry"
        if self.homograph:
            print "\n".join([cmd('homograph',self.homograph), cmd('headword',self.word)]).encode('utf-8') 
        else:
            if self.anchor:
                print hypercmd('headword',self.anchor,self.word).encode('utf-8')
            else:
                print cmd('headword',self.word).encode('utf-8') 
        
    
#class POS():
    #def __init__(self,p): 
        #try:
            #self.pos = p.find('.//Run').text 
        #except AttributeError:
            #self.pos = '{\\fixpos}'
        
    #def toLatex(self): 
        #print cmd('pos',self.pos, indent=1).encode('utf-8')
  
    
class Pronunciation():
    def __init__(self,p): 
        self.ipa = p.find('.//Run').text 
        self.anchor = p.attrib.get('id',False)
        
    def toLatex(self): 
        latexipa = self.ipa.replace(u'ꜜ','{\downstep}')
        if self.anchor:
            print hypercmd('ipa',self.anchor, latexipa, indent=1).encode('utf-8')
        else:
            print cmd('ipa', latexipa, indent=1).encode('utf-8')
    
class Sense():
    def __init__(self,s):
        self.anchor = s.attrib.get('id',False)
        self.definition = getText(s,'LexSense_Definition','AStr')
        try:
          self.definition = self.definition.strip()
        except AttributeError:
          pass
        self.examples = [Example(x) for x in s.findall('.//LexExampleSentence')]     
        self.references = [LexReflink(l) for l in (s.findall('.//LexReferenceLink'))]
        self.scientificname = getText(s,'LexSense_ScientificName','Str')
        self.usagetypes = [a.attrib.get('abbr', None) for a in (s.findall('LexSense_UsageTypes/Link/Alt'))]
        self.lfg = getText(s,'LexSense_lexical_function_glosses','Str')
        self.synpos = getText(s,'MoMorphSynAnalysisLink_MLPartOfSpeech','AStr')
        self.lsgloss = getText(s,'LexSense_Gloss','AStr') 
    
    def toLatex(self,number=False):
        if number:
            print cmd('sensenr',number,indent=1)
        if self.synpos:
            print cmd('synpos',self.synpos,indent=2).encode('utf-8')
        if self.definition:
            if self.anchor:
                print hypercmd('definition',self.anchor,self.definition,indent=3).encode('utf-8')
            else:
                print cmd('definition',self.definition,indent=3).encode('utf-8')
        if self.lsgloss:
            print cmd('lsgloss',self.lsgloss,indent=3).encode('utf8')
        if len(self.examples) == 1:
            print '{\\startexample}%'
            self.examples[0].toLatex()
        elif len(self.examples) > 1:
            print '{\\startexample}'
            for i,example in enumerate(self.examples): 
                example.toLatex(number=i+1)
        for r in self.references:
            r.toLatex()
        if self.scientificname:
            print "%s\n{\\definitioncloser}" % cmd('sciname',self.scientificname)
        else:
          if len(self.examples) == 0: #examples come with their own punctuation
            print "{\\definitioncloser}"
        for u in self.usagetypes:
            print cmd('usage',u)
        #if self.synpos:
            #print cmd('pos',self.synpos)
        #if self.lsgloss:
            #print cmd('lsgloss',self.lsgloss)
          
 
  
class Example():
    def __init__(self,x):
        self.anchor = x.attrib.get('id',False)
        self.vernacular = False
        try:
            self.vernacular = x.find('.//LexExampleSentence_Example').find('.//Run').text 
            self.translations = [Translation(t) for t in x.findall('.//CmTranslation')]
        except AttributeError:
            pass
      
    def toLatex(self,number=False):
        if self.vernacular:
            if number:
                print cmd('exnr',number,indent=5)
            modvernacular = hyphenate(self.vernacular)
            if self.anchor:
                print hypercmd('vernacular',self.anchor,self.vernacular,indent=6).encode('utf-8') 
                print hypercmd('modvernacular',self.anchor,modvernacular,indent=6).encode('utf-8') 
            else:
              print cmd('vernacular',self.vernacular,indent=6).encode('utf-8')
              print cmd('modvernacular',modvernacular,indent=6).encode('utf-8')
            for t in self.translations: 
                t.toLatex()
          

class Translation():
    def __init__(self,t):
        self.string = t.find('.//Run').text 
        self.anchor = t.attrib.get('id',False)
    
    def toLatex(self):
        if self.anchor:
            print hypercmd('trs',self.anchor,self.string, indent=6).encode('utf-8')
        else:
            print cmd('trs',self.string,indent=6).encode('utf-8')
          
        


class Etymology ():
      def __init__(self,e):
        self.form = False
        self.gloss = False
        self.source = False
        if e == None:
          return
        self.form = getText(e,'LexEtymology_Form','AStr')
        self.gloss = getText(e,'LexEtymology_Gloss','AStr')
        src = e.find('LexEtymology_Source/AUni')
        if src != None:
          self.source = src.text
  
      def toLatex(self):
          if self.form or self.gloss or self.source:
              print cmd('etymology','',indent=6).encode('utf-8')
          if self.source:
              print cmd('etymologysrc',self.source,indent=8).encode('utf-8')
          if self.form:
              print cmd('etymologyform',self.form,indent=8).encode('utf-8')
          if self.gloss:
            print cmd('etymologygloss',self.gloss,indent=8).encode('utf-8')
          if self.form or self.gloss or self.source:
            print cmd('etymologycloser','',indent=6).encode('utf-8')
          

class MimimalLexReferences():
      def __init__(self,e):
          if e == None:
            self.lexreflinks = []
          else:
            self.lexreflinks = [LexReflink(lrl) for lrl in e.findall('LexReferenceLink')]
          
      def toLatex(self):
          for l in self.lexreflinks:
              l.toLatex()
        
class LexReflink():
    def getTargets(self,l):
      t = l.attrib['target']
      try:
        s = l.find('Alt').attrib.get('sense')
      except AttributeError:
        s = False
      return (t,s)
  
    def __init__(self,e):
          if e == None:
            self.type_ = False
            self.targets = []
            return
          self.type_ = e.find('LexReferenceLink_Type/Link/Alt').attrib.get('abbr')
          #if self.type_ == None:
            #self.type_ = e.find('LexReferenceLink_Type/Link/Alt').attrib.get('revabbr')          
          try:
            self.type_ = self.type_.replace('.','').replace(' ','')
          except AttributeError:
            self.type_='empty'
          self.targets = [self.getTargets(l) for l in e.findall('LexReference_Targets/Link')]  

    def toLatex(self):
        targets = []
        for t,s in self.targets:
          if not s:
              try:
                s = linkd[t]
              except KeyError:
                s = '\\error{No label for link!}'        
          #take care of homographs
          s = re.sub('(.*[^ 0-9])([0-9]+)',r'\\textsuperscript{\2}\1', s)        
          #take care of sense numbers
          s = re.sub('(.*[^ 0-9]) ([0-9]+)$',r'\1\\textsuperscript{\2}', s)
          targets.append("\hyperlink{%s}{%s}"%(t,s))        
        print cmd('type%s'%self.type_,'; '.join(targets)).encode('utf8')

class VariantFormEntryBackRefs ():
      def __init__(self,e):
          if e == None:
            self.lexentryreflinks = []
            return #FIXME
          self.lexentryreflinks = [LexEntryReflink(lerl) for lerl in e.findall('LexEntryRefLink')]
      
      def toLatex(self):
        if len(self.lexentryreflinks)>0:
          print cmd('varblockopener','')
        print ', '.join([l.prepareLatex() for l in self.lexentryreflinks]).encode('utf8')+'%'         
        if len(self.lexentryreflinks)>0:
          print cmd('varblockcloser','')

class VisibleVariantEntryRef ():
      def __init__(self,e): 
          if e==None:
            self.lexentryreflinks = []
            return
          
          self.lexentryreflinks = [LexEntryReflinkV(lerlv) for lerlv in e.findall('LexEntryRefLink')]
      
      def toLatex(self):
          if len(self.lexentryreflinks)>0:
            print cmd('varofblockopener','')
          print ','.join([l.prepareLatex() for l in self.lexentryreflinks]).encode('utf8')+'%'            
          if len(self.lexentryreflinks)>0:
            print cmd('varofblockcloser','')
        
        
class LexEntryReflink():
    def __init__(self,e):
          self.target = e.find('LexEntryRefLink_OwningEntry/Link').attrib['target']
          self.alt = e.find('LexEntryRefLink_OwningEntry/Link/Alt').attrib['entry']
          try:
            self.vet = e.find('LexEntryRef_VariantEntryTypes/Link/Alt').attrib['revabbr']
          except AttributeError:
            self.vet='empty'
          self.vet=self.vet.replace('.','').replace(' ','')
          
    def prepareLatex(self):
          latexalt = re.sub('(.*)([0-9]+)$',r'\\textsuperscript{\2}\1', self.alt)
          #latexalt = self.alt.replace('1','\\textsuperscript{1}')
          latexalt = hyphenate(latexalt)
          s = "\\type%s{\hyperlink{%s}{%s}}"%(self.vet,self.target,latexalt)
          return s
        
         

class LexEntryReflinkV():
    def __init__(self,e):
          self.target = e.attrib.get('target','\\error{no target}')
          try:
            self.vet = e.find('LexEntryRef_VariantEntryTypes/Link/Alt').attrib['abbr']
          except AttributeError:
            self.vet=''          
          self.vet=self.vet.replace('.','').replace(' ','')
          self.cl = e.find('LexEntryRef_ComponentLexemes/Link').attrib['target']
            
          
    def prepareLatex(self):
          s = " \\type%s{\hyperlink{%s}{%s}}"%(self.vet,
                                              self.cl,
                                              hyphenate(linkd[self.cl]))
          return s
            
                

#===================

fn = sys.argv[1]
tree = etree.parse(fn)
root = tree.getroot()

lexentries = []

for entry in root.findall('.//LexEntry'):
  lexentries.append(LexEntry(entry))
  
 
linkd = {}
for le in lexentries:
  ID = le.ID
  headword = le.headword.word 
  linkd[le.ID] = headword
   

for le in lexentries:
  print "%"+30*"-"
  le.toLatex()
  #print le.headword.word
  #print le.headword.homograph
  #try:
    #print le.senses[0].definition
  #except:
    #pass
  