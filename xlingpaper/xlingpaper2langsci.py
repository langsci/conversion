import sys
import xml.etree.ElementTree as ET

class lingPaper():
  def __init__(self,el):
    self.chapters = [chapter(c) for c in el.findall('chapter')]
    self.frontmatter = el.find('frontmatter')
    self.backmatter = el.findall('backmatter')  
    
  def __str__(self):   
    return '\n'.join([str(ch) for ch in self.chapters])

class paragraph():
  def __init__(self,el):
    self.el = el
    self.tag = el.tag 
    self.text = el.text
  
class figure():
  def __init__(self,el):
    self.el = el
    self.tag = el.tag 
    self.text = el.text    
  
class example():
  def __init__(self,el):
    self.el = el
    self.tag = el.tag 
    self.text = el.text
  
class tablenumbered():
  def __init__(self,el):
    self.el = el
    self.tag = el.tag 
    self.text = el.text
  

class genericsection():
  def __init__(self,el):
    self.el = el
    self.tag = el.tag
    self.ID = el.attrib["id"]
    self.title = el.find("secTitle").text 
    if self.title == None:
      self.title = ''
    self.preamble = self.getPreamble() 
    self.subsections = self.getSubsections()
    self.sectionlevel = False
    self.sectionlevel = self.setLevel() 
    
    
  def getPreamble(self):
    children4preamble = []
    for ch in self.el:      
      if ch.tag == 'secTitle':
        continue      
      if ch.tag != self.getNextXMLLevel():
        children4preamble.append(ch)
      else:
        break
    return [self.treatelement(el) for el in children4preamble]
      
    
  def treatelement(self,el):
    if el.tag=='p':
      return paragraph(el)
    if el.tag=='figure':
      return figure(el)
    if el.tag=='example':
      return example(el)
    if el.tag=='tablenumbered':
      return tablenumbered(el)
    raise ValueError
    
    
  def getSubsections(self):
    pass
  
  def setLevel(self):
    pass
   
  def title2latex(self):
    return "\\%s{%s}\\label{sec:%s}\n" %(self.sectionlevel,self.title,self.ID)
  
  def __str__(self):
    titlestring = self.title2latex()
    preamblestring = ''
    if self.preamble:
      preamblestring = ' '.join(["%s"%el.text for el in self.preamble])
    subsectionstring =  '\n'.join([str(ch) for ch in self.subsections])
    return '\n'.join([titlestring,preamblestring,subsectionstring])
  
class chapter(genericsection):
  
  def setLevel(self):
    return 'chapter'
   
  def getNextXMLLevel(self): 
    return 'section1'
    
  def getSubsections(self):
    return [section1(s) for s in self.el.findall('section1')]
  
  #def __str__(self):
    #return str(title)
  
  
class section1(genericsection):
  def setLevel(self):
    return 'section'
  
  def getNextXMLLevel(self): 
    return 'section2'
    
  def getSubsections(self):
    return [section2(s) for s in self.el.findall('section2')]
  
  
  
class section2(genericsection):
  
  def setLevel(self):
    return 'subsection'
      
  def getNextXMLLevel(self): 
    return 'section3'
  
  def getSubsections(self):
    return self.el.findall('section3')
  
    
  
    
if __name__ == "__main__":
  fn = sys.argv[1]
  print(fn)
  tree = ET.parse(fn)
  root = tree.getroot()
  doc = lingPaper(root)
  print(doc)

