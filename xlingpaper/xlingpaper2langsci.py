import sys
import xml.etree.ElementTree as ET

class lingPaper():
    """A representation of the complete paper """

    def __init__(self, el):
        self.chapters = [chapter(c) for c in el.findall('chapter')]
        backmatter = el.find('backMatter')
        self.appendices = [chapter(c) for c in backmatter.findall('appendix')]
        self.frontmatter = el.find('frontmatter')
        self.backmatter = el.findall('backmatter')

    def __str__(self):
        return '%s%s'%('\n'.join([str(ch) for ch in self.chapters]),
                       '\n'.join([str(ch) for ch in self.appendices]),
                      )




class genericsection():
    """A portion of a paper, which can contain subsections"""

    def __init__(self, el):
        self.el = el
        self.tag = el.tag
        self.ID = el.attrib["id"]
        self.title = el.find("secTitle").text
        if self.title is None:
            self.title = ''
        self.preamble = self.getPreamble()
        self.subsections = self.getSubsections()
        self.sectionlevel = False
        self.sectionlevel = self.setLevel()
  
    def getSubsections(self):
        pass

    def setLevel(self):
        pass

    def getNextXMLLevel(self):
        pass

    def getPreamble(self):
        """
        Get the content of the section before the first subsection.
        If no subsections are present, preamble is everything
        """

        children4preamble = []
        for ch in self.el:
            if ch.tag == 'secTitle':
                continue
            if ch.tag != self.getNextXMLLevel():
                children4preamble.append(ch)
            else:
                break
        return [textelement(el) for el in children4preamble]

    def title2latex(self):
        return "\\%s{%s}\\label{sec:%s}\n" %(self.sectionlevel, self.title, self.ID)

    def __str__(self):
        titlestring = self.title2latex()
        preamblestring = ''
        if self.preamble:
            preamblestring = ' '.join(["%s"%el.text for el in self.preamble])
        subsectionstring = '\n'.join([str(ch) for ch in self.subsections])
        return '\n'.join([titlestring, preamblestring, subsectionstring])



class chapter(genericsection):
    """A section of the chapter level"""

    def setLevel(self):
        return 'chapter'

    def getNextXMLLevel(self):
        return 'section1'

    def getSubsections(self):
        return [section1(s) for s in self.el.findall('section1')]



class section1(genericsection):
    """A section of the section1 level"""
    def setLevel(self):
        return 'section'

    def getNextXMLLevel(self):
        return 'section2'

    def getSubsections(self):
        return [section2(s) for s in self.el.findall('section2')]



class section2(genericsection):
    """A section of the section2 level"""

    def setLevel(self):
        return 'subsection'

    def getNextXMLLevel(self):
        return 'section3'

    def getSubsections(self):
        return [section3(s) for s in self.el.findall('section3')]


class section3(genericsection):
    """A section of the section3 level"""

    def setLevel(self):
        return 'subsubsection'

    def getNextXMLLevel(self):
        return 'section4'

    def getSubsections(self):
        return [section4(s) for s in self.el.findall('section4')]



class textelement():
    """An XML element found in an XLingPaper"""

    def __init__(self, el):
        self.el = el
        self.tag = el.tag
        self.text = self.getText(el)

    def getText(self, el): 
        """Return the text for an xml element"""
        
        if self.tag in ('p', 'pc', 'figure', 'example', 'chart', 'tablenumbered', 'table'):
            #this element causes special markup to be inserted in addition to its textual content
            return self.treatTextElement(el)
        else:
            #the element does not have meaning beyond the sum of the text of its children
            return "".join([self.treatTextElement(te) for te in self.el.iter() if te != el])


    def treatTextElement(self, te):
        """output LaTeX code according to tag of XML element"""
                
        def prettify_latex(s):
            """adjust XML text to LaTeX convention"""
            
            return s.replace('%', r'\%')\
                .replace('{', r'\ob ')\
                .replace('}', r'\cb ')\
                .replace('&', r'\&')\
                .replace('#', r'\#')\
                .replace('_', r'\_')
            
        tail = ''
        text = ''
        if te.tail:
            tail = prettify_latex(te.tail)
            if tail[-1].strip() == '': #replace all trailing white space by ' '
                tail = "%s "%tail.strip()
        if te.text:
            text = prettify_latex(te.text)
        if te.tag == 'caption':
            return '\n%%\\caption{%s}%s\n'%(text, tail)
        if te.tag == 'free':
            return '\\glt %s %s'%(text, tail)
        if te.tag in    ('td', 'th'):
            colspan = te.attrib.get('colspan')
            if colspan:
                return r'\multicolumn{%s}{l}{%s %s} & %s'%(colspan,
                                                           text,
                                                           ''.join([self.treatTextElement(x)
                                                                    for x
                                                                    in te]),
                                                           tail)
            return '%s %s & %s'%(text, ''.join([self.treatTextElement(x) for x in te]), tail)
        if te.tag == 'chart':
            return ''.join([self.treatTextElement(x) for x in te])
        if te.tag == 'interlinear':
            return ''.join([self.treatTextElement(x) for x in te])
        if te.tag == 'single':
            return ''.join([self.treatTextElement(x) for x in te])
        if te.tag == 'img':
            return '%%\\includegraphics[width=\\textwidth]{%s}\n'%te.attrib['src']
        if te.tag == 'object':
            typ = te.attrib["type"]
            if typ == 'tItalic':
                return '\\textit{%s}%s'%(text, tail)
            if typ == 'tBold':
                return '\\textbf{%s}%s'%(text, tail)
            if typ == 'tSuperscript':
                return '\\textsuperscript{%s}%s'%(text, tail)
            if typ == 'tSubscript':
                return '\\textsubscript{%s}%s'%(text, tail)
            if typ == 'tUnderline':
                return '\\ul{%s}%s'%(text, tail)
        if te.tag == 'langData':
            lang = te.attrib["lang"]
            if lang in('lVernacular',
                       'lVernacularProse',
                       "lVernacularHeader",
                       "lAppendixHeader",
                       "lAppendLabel"):
                return '\\vernacular{%s}%s'%(text, tail)
            if lang in ('lGloss', 'lGlossProse', 'lGlossHeader'):
                return '\\gloss{%s}%s'%(text, tail)
            if lang in ('lRule', 'lRuleHeader'):
                return '\\regel{%s}%s'%(text, tail)
            if lang in ('lExampleHeader', "lDerivationHeader"):
                return '%s%s'%(text, tail)
        if te.tag == 'gloss':
            lang = te.attrib["lang"]
            if lang in ('lGloss', 'lGlossProse'):
                return '\\gloss{%s}%s'%(text, tail)
        if te.tag == 'exampleRef':
            label = te.attrib.get('num')
            return '\\REF{ex:%s} %s'% (label, tail)
        if te.tag == 'figureRef':
            label = te.attrib.get('figure')
            return '\\figref{ex:%s} %s'% (label, tail)
        if te.tag == 'sectionRef':
            label = te.attrib.get('sec')
            return '\\sectref{sec:%s} %s'% (label, tail)
        if te.tag == 'appendixRef':
            label = te.attrib.get('app')
            return '\\appref{sec:%s} %s'% (label, tail)
        if te.tag == 'endnoteRef':
            label = te.attrib.get('note')
            return '\\fnref{fn:%s} %s'% (label, tail)
        if te.tag == 'tablenumberedRef':
            label = te.attrib.get('table')
            return '\\tabref{tab:%s} %s'% (label, tail)
        if te.tag == 'citation':
            key = te.attrib.get('ref')
            return '\\citealt{%s} %s'% (key, tail)
        if te.tag == 'link':
            key = te.attrib.get('href')
            return '\\href{%s}{%s}%s'% (key, text, tail)
        if te.tag == 'lineGroup':
            numberoflines = len(te)
            lls = numberoflines * 'l' #count how many src/imt lines there are
            return '\\g%s %s '% (lls, ''.join([self.treatTextElement(x) for x in te]))
        if te.tag == 'line':
            langDatas = [x.text for x in te.findall('.//langData')] #langData can be nested in <wrd>
            if len(langDatas) > 0:
                return ' '.join(langDatas)+'\\\\\n'
            glosses = [x.text for x in te.findall('.//gloss')] #gloss can be nested in <wrd>
            if len(glosses) > 0:
                return ' '.join(glosses)+'\\\\\n'
            return '\\\\%%no interlinear content in XML\n'
        if te.tag == 'table':
            return self.treattabular(te)
        if te.tag == 'figure':
            label = te.attrib.get('id', False)
            labelstring = ''
            if label:
                labelstring = '\\label{fig:%s} '%label
            figurebody = ' '.join([self.treatTextElement(x) for x in te])
            return '\n\n\\begin{figure}\n%s%s\n\\end{figure}\n\n' % (figurebody, labelstring)
        if te.tag == 'tablenumbered':
            label = te.attrib.get('id', False)
            labelstring = ''
            if label:
                labelstring = '\\label{tab:%s} '%label
            tablebody = ' '.join([self.treatTextElement(x) for x in te])
            return '\n\n\\begin{table}\n%s%s\n\\end{table}\n\n' % (tablebody, labelstring)
        if te.tag == 'tr':
            trbody = ' '.join([self.treatTextElement(x) for x in te])
            return '%s\\\\\n' % (trbody)
        if te.tag == 'p' or te.tag == 'pc':
            text = ' '
            try:
                text = prettify_latex(te.text)
            except AttributeError:
                pass
            return "%s %s\n\n" %(text, ''.join([self.treatTextElement(x) for x in te]))
        if te.tag == 'example':
            label = te.attrib.get('num', False)
            labelstring = ''
            if label:
                labelstring = '\\label{ex:%s} '%label
            exbody = ''.join([self.treatTextElement(x) for x in te])
            return '\n\\ea%s\n%s\n\\z\n\n' % (labelstring, exbody)
        if te.tag == 'exampleHeading':
            text = ' '
            try:
                text = self.latex_prettify(te.text)
            except AttributeError:
                pass
            return "%s %s\n\n" %(text, ''.join([self.treatTextElement(x) for x in te]))
        if te.tag == 'endnote':
            label = te.attrib.get('id', False)
            labelstring = ''
            if label:
                labelstring = '\\label{fn:%s} '%label
            fnbody = ' '.join([self.treatTextElement(x) for x in te])
            return '\\footnote{%s%s\n}%%\n' % (labelstring, fnbody)
        if te.text is None:
            return ''
        if te.tag == 'textInfo':
            return ''
        if te.tag == 'textTitle':
            return '%%\\title{%s}'%te.text
        if te.tag == 'shortTitle':
            return te.text
        print(te, te.tag, te.text, te.tail, te.attrib)
        raise ValueError #an unknown tag was provided
        return te.text #unreachable

    def treattabular(self, el):
        "parse XML tabular and output latex tabular"
        numberofcolumns = sum([int(td.attrib.get('colspan', 1)) for td in el.find('tr')])+1
        #numberofcolumns = len(el.find('tr'))+1 #hack to take care of extra & at end #TODO
        columntypes = numberofcolumns * 'l'
        try:
            caption = el.find('caption').text
        except AttributeError:
            caption = '\\nocaption'
        trs = el.findall('tr')
        rows = ''.join([self.treatTextElement(tr) for tr in trs])
        return """\n\\begin{tabular}{%s}
    %s\\end{tabular}
%%\\caption{%s}
        """%(columntypes, rows, caption) #hack with % sign comment #FIXME


if __name__ == "__main__":
    fn = sys.argv[1]
    print('%% converted from', fn)
    tree = ET.parse(fn)
    root = tree.getroot()
    doc = lingPaper(root)
    print(doc)
