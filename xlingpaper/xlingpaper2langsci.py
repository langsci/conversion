import sys
import xml.etree.ElementTree as ET

class lingPaper():
  def __init__(self,el):
    self.chapters = [chapter(c) for c in el.findall('chapter')]
    self.frontmatter = el.find('frontmatter')
    self.backmatter = el.findall('backmatter')  
    
  def __str__(self):   
    return '\n'.join([str(ch) for ch in self.chapters])
 

class textelement():
  def __init__(self,el):
    self.el = el
    self.tag = el.tag 
    self.text = self.getText(el)
    
  def getText(self,el):  
    return "".join([self.treatTextElement(te) for te in  self.el.iter() if te!=el])
  
  def treatTextElement(self,te):
    tail = ''
    text = ''
    if te.tail:
      tail = te.tail
      if tail[-1].strip() == '': #replace all trailing white space by ' '
        tail = "%s "%tail.strip()
    if te.text:
      text = te.text
    if te.tag == 'object':
      typ = te.attrib["type"]
      if typ == 'tItalic':
        return '\\textit{%s}%s'%(text,tail)
    if te.tag == 'langData':
      lang = te.attrib["lang"]
      if lang == 'lVernacular':
        return '\\vernacular{%s}%s'%(text,tail) 
    if te.tag == 'gloss':
      lang = te.attrib["lang"]
      if lang == 'lGloss':
        return '\\gloss{%s}%s'%(text,tail) 
    if te.tag == 'caption':
        return '\n%%\\caption{%s}%s\n'%(text,tail)  
    if te.tag == 'free':
        return '\\glt %s %s'%(text,tail)  
    if te.tag == 'td':
        return '%s %s & %s'%(text,''.join([self.treatTextElement(x) for x in te]) ,tail)         
    if te.tag == 'th':
        return '%s %s & %s'%(text,''.join([self.treatTextElement(x) for x in te]) ,tail)  
    if te.tag == 'chart':
        return ''.join([self.treatTextElement(x) for x in te]) 
    if te.tag == 'interlinear':
        return ''.join([self.treatTextElement(x) for x in te])   
    if te.tag == 'img':
        return '\\includegraphics[width=\\textwidth]{ %s}'%te.attrib['src']
    if te.tag == 'lineGroup':
        numberoflines = len(te)
        lls = numberoflines * 'l' #count how many src/imt lines there are
        return '\\g%s %s '% (lls,  ''.join([self.treatTextElement(x) for x in te]) )
    if te.tag == 'line':   
        try:
          linebody = te.find('langData').text #check for embedded elements
        except AttributeError:
          linebody = te.find('gloss').text #check for embedded elements          
        return '1%s2\\\\\n'% linebody
    if te.tag == 'table':        
        return self.treattabular(te)
    if te.tag == 'figure':  
      label = te.attrib.get('id', False) 
      labelstring = ''
      if label:
        labelstring = '\\label{fig:%s} '%label 
      figurebody = ' '.join([self.treatTextElement(x) for x in te])
      return '\n\n\\begin{ figure}\n%s%s\n\\end{ figure}\n\n' % (figurebody,labelstring)   
    
    if te.tag == 'tablenumbered':  
      label = te.attrib.get('id', False) 
      labelstring = ''
      if label:
        labelstring = '\\label{tab:%s} '%label 
      tablebody = ' '.join([self.treatTextElement(x) for x in te])
      return '\n\n\\begin{ table}\n%s%s\n\\end{ table}\n\n' % (tablebody,labelstring)   
    if te.tag == 'tr':   
        trbody = ' '.join([self.treatTextElement(x) for x in te])
        return '%s\\\\\n' % (trbody)   
    if te.tag == 'p':  
        text = ' '
        try:
          text=te.text.strip()
        except AttributeError:
          pass 
        return "%s %s\n\n" %(text, ''.join([self.treatTextElement(x) for x in te]))
    if te.tag == 'exampleRef': 
      label  = te.attrib.get('num')
      return '\\REF{ ex:%s} %s'% (label, tail)   
    if te.tag == 'figureRef': 
      label  = te.attrib.get('figure')
      return '\\figref{ ex:%s} %s'% (label, tail)
    if te.tag == 'sectionRef': 
      label  = te.attrib.get('sec')
      return '\\sectref{ sec:%s} %s'% (label, tail)
    if te.tag == 'tablenumberedRef': 
      label  = te.attrib.get('table')
      return '\\tabref{ ex:%s} %s'% (label, tail)
    if te.tag == 'citation': 
      key  = te.attrib.get('ref')
      return '\\citealt{%s} %s'% (key, tail)
    if te.tag == 'example': 
      label = te.attrib.get('num', False) 
      labelstring = ''
      if label:
        labelstring = '\\label{ex:%s} '%label 
      exbody = ''.join([self.treatTextElement(x) for x in te])
      return '\n\\ea%s\n%s\n\\z\n\n' % (labelstring, exbody)   
    if te.tag == 'endnote':        
        label = te.attrib.get('id', False)
        labelstring = ''
        if label:
          labelstring = '\\label{fn:%s} '%label
        fnbody = ' '.join([self.treatTextElement(x) for x in te])
        return '\\footnote{%s%s\n}%%\n' % (labelstring, fnbody)
    if te.text == None:
      return ''  
    print(te,te.text)
    raise ValueError
    return te.text
  
  def treattabular(self,el):
    numberofcolumns = len(el.find('tr'))+1 #hack to take care of extra & at end #TODO
    columntypes = numberofcolumns * 'l'
    caption = el.find('caption').text
    trs = el.findall('tr')
    rows = ''.join([self.treatTextElement(tr) for tr in trs])      
    return """\n\\begin{ tabular}{%s}  
  %s\\end{ tabular}
\\caption{%s}
    """%(columntypes,rows,caption)
  
class paragraph(textelement):
  def getText(self,el):  
    return self.treatTextElement(el)
  
  
class figure(textelement):
  def getText(self,el):  
    return self.treatTextElement(el)

  
class example(textelement):   
  def getText(self,el):  
    return self.treatTextElement(el)

class chart(textelement):
  def getText(self,el):  
    return self.treatTextElement(el)
  
class tablenumbered(textelement):
  def getText(self,el):  
    return self.treatTextElement(el)

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
    #print(self.tag,len(children4preamble))
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
    if el.tag=='chart':
      return chart(el)
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

