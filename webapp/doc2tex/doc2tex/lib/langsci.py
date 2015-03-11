import os
import re
import shutil
import codecs
import uuid
import sys 

wd = '/home/doc2tex'
wd = '/tmp'
lspskeletond = '/home/doc2tex/skeletonbase'
#lspskeletond = '/home/snordhoff/versioning/git/langsci/lsp-converters/webapp/doc2tex/assets/skeletonbase'
#wwwdir = os.path.join(wd,'www')
wwwdir = '/var/www/wlport'	


def convert(fn):
    #print "converting %s" %fn
    odtfn = False
    #os.chdir(wd)
    #tmpdir = fn.split('/')[-2] 
    tmpdir = "."
    #print tmpdir
    if fn.endswith("docx"):	
	#os.chdir(tmpdir)
	syscall = """soffice --headless --outdir %s --convert-to odt "%s"  """ %(tmpdir,fn)
	#print syscall
	os.system(syscall)
	odtfn = fn.replace("docx","odt") 
    elif fn.endswith("doc"):	
	#os.chdir(tmpdir)
	syscall = """soffice --headless --outdir %s --convert-to odt "%s"  """ %(tmpdir,fn)
	#print syscall
	os.system(syscall)
	odtfn = fn.replace("doc","odt")
    elif fn.endswith("odt"):
	odtfn = fn 
    else:
	raise ValueError
    if odtfn == False:
	return False
    #os.chdir(wd)
    texfn = odtfn.replace("odt","tex")
    print texfn
    w2loptions = ("-clean",
    "-wrap_lines_after=0",
    "-multilingual=false", 
    #floats
    "-simple_table_limit=10"
    "-use_supertabular=false",
    "-float_tables=false", 
    "-float_figures=false", 
    "-use_caption=true", 
    '-image_options="width=\\textwidth"',
    #"use_colortbl=true",
    #"original_image_size=true",
    #input
    "-inputencoding=utf8",
    "-use_tipa=false", 
    "-use_bibtex=true", 
    "-ignore_empty_paragraphs=true",
    "-ignore_double_spaces=false", 
    #formatting
    "-formatting=convert_most",
    "-use_color=false",
    "-page_formatting=ignore_all",
    "-use_hyperref=true",
    #"-no_preamble=true"
    )
    syscall = """w2l {} "{}" "{}" """.format(" ".join(w2loptions), odtfn, texfn)
    print syscall
    os.system(syscall)
    w2lcontent = open(texfn).read().decode('utf8')
    preamble, text = w2lcontent.split(r"\begin{document}")
    text = text.split(r"\end{document}")[0] 
    preamble=preamble.split('\n')
    newcommands = '\n'.join([l for l in preamble if l.startswith('\\newcommand') and '@' not in l and 'writerlist' not in l and 'labellistLi' not in l and 'textsubscript' not in l]) # or l.startswith('\\renewcommand')])
    #replace all definitions of new environments by {}{}
    newenvironments = '\n'.join(['%s}{}{}'%l.split('}')[0] for l in preamble if l.startswith('\\newenvironment')  and 'listLi' not in l]) # or l.startswith('\\renewcommand')])
    newpackages = '\n'.join([l for l in preamble if l.startswith('\\usepackage')])
    newcounters = '\n'.join([l for l in preamble if l.startswith('\\newcounter')])        
    return Document(newcommands,newenvironments, newpackages, newcounters, text)
    
class Document:
    def __init__(self, commands, environments, packages, counters, text):
	self.commands = commands
	self.environments = environments
	self.packages = packages
	self.counters = counters
	self.text = text
	self.modtext = self.getModtext()
	
    def ziptex(self): 
	localskeletond = os.path.join(wd,'skeleton')
	try:
	   shutil.rmtree(localskeletond)
	except OSError:
	    pass
	shutil.copytree(lspskeletond, localskeletond)
	os.chdir(localskeletond)
	localcommands = codecs.open('localcommands.sty','a', encoding='utf-8')
	localpackages = codecs.open('localpackages.sty','a', encoding='utf-8')
	localcounters = codecs.open('localcounters.sty','a', encoding='utf-8') 
	content =   codecs.open('chapters/filename.tex','w', encoding='utf-8') 
	contentorig =   codecs.open('chapters/filenameorig.tex','w', encoding='utf-8')  
	localcommands.write(self.commands)
	localcommands.write(self.environments)
	localcommands.close()
	localpackages.write(self.packages)
	localpackages.close()
	localcounters.write(self.counters)
	localcounters.close()
	content.write(self.modtext)
	content.close()
	contentorig.write(self.text)
	contentorig.close()
	os.chdir(wd)
	self.zipfn = str(uuid.uuid4())
	shutil.make_archive(self.zipfn, 'zip', localskeletond)
	shutil.move(self.zipfn+'.zip',wwwdir) 
	
	
	
    def getModtext(self):
	modtext = self.text
	explicitreplacements = (("{\\textquoteleft}","`"),
				("{\\textquotedblleft}","``"), 
				("{\\textquoteright}","'"),
				("{\\textquotedblright}","''"),
				("{\\textquotesingle}","'"),
				("{\\textquotedouble}",'"'), 
				("\\par}","}"),
				("\\clearpage","\n"),
				#("\\begin","\n\\begin"),
				#("\\end","\n\\end"), 
				#(" }","} "),%causes problems with '\ '
				("supertabular","tabular"),  
				("\~{}","{\\Tilde}"), 
				("\\section","\\chapter"),  
				("\\subsection","\\section"),  
				("\\subsubsection","\\subsection"),  
				
				("""\\begin{listWWNumiileveli}
\\item 
\\setcounter{listWWNumiilevelii}{0}
\\begin{listWWNumiilevelii}
\\item 
\\begin{styleLangSciLanginfo}""","\\begin{styleLangSciLanginfo}"),#MS
				("""\\begin{listLangSciLanginfoiileveli}
\\item 
\\begin{styleLangSciLanginfo}""","\\begin{styleLangSciLanginfo}"),#OOi
				("""\\begin{listLangSciLanginfoiilevelii}
\\item 
\\begin{styleLangSciLanginfo}""","\\begin{styleLangSciLanginfo}"),#OOii
				("""\\end{styleLangSciLanginfo}


\\end{listWWNumiilevelii}
\\end{listWWNumiileveli}""","\\end{styleLangSciLanginfo}"),				
				("\\begin{styleLangSciLanginfo}\n","\\ea\label{ex:}\n\\langinfo{}{}{"),
				("\n\\end{styleLangSciLanginfo}\n","}\\\\\n"),
				#("\\begin{styleLangSciExample}\n","\\ea\label{ex:}\n\\gll "),
				("\\begin{styleLangSciExample}\n","\n\\gll "),
				("\\end{styleLangSciExample}\n","\\\\"),
				("\\begin{styleLangSciSourceline}\n","\\gll "),
				("\\end{styleLangSciSourceline}\n","\\\\"),
				("\\begin{styleLangSciIMT}\n","     "),
				("\\end{styleLangSciIMT}\n","\\\\"),
				("\\begin{styleLangSciTranslation}\n","\\glt "),
				("\\end{styleLangSciTranslation}","\z"), 
				("\\begin{styleLangSciTranslationSubexample}\n","\\glt "),
				("\\end{styleLangSciTranslationSubexample}","\z\n%%1st subexample: change \\ea to \\ea\\ea; remove \\z\n%%further subexamples: change \\ea to \\ex; remove \\z\n%%last subexample: change \\z to \\z\\z"), 
				("""\\setcounter{listWWNumiileveli}{0}
\\ea\\label{ex:}""",""),#MS
				#("""\\setcounter{listLangSciLanginfoiilevelii}{0}
#\\ea\\label{ex:}""",""),#OO
				("""\\begin{listLangSciLanginfoiileveli}
\item""","\\ea\label{ex:}"),
				("""\setcounter{listLangSciLanginfoiilevelii}{0}
\\ea\label{ex:}""",""),
				("\n\\end{listLangSciLanginfoiileveli}",""), 
				("\n\\end{listLangSciLanginfoiilevelii}",""), 
				#end examples
				("{styleQuote}","{quote}"),  
				("{styleAbstract}","{abstract}"),  
				("textstyleLangSciCategory","textsc"),  
				("\\begin{styleListParagraph}","%\\begin{epigram}"),
				("\\end{styleListParagraph}","%\\end{epigram}"), 
				("\\begin{styleListenabsatz}","%\\begin{epigram}"),
				("\\end{styleListenabsatz}","%\\end{epigram}"), 
				("\\begin{styleEpigramauthor}","%\\begin{epigramauthor}"),
				("\\end{styleEpigramauthor}","%\\end{epigramauthor}"),  
				("{styleConversationTranscript}","{lstlisting}"),   
				("\ "," "),  
				#(" }","} "),  
				("\\setcounter","%\\setcounter"),  
				
			    )    
	yanks =  ("\\begin{flushleft}",
		    "\\end{flushleft}",
		    "\\centering",
		    "\\tablehead{}", 
		    "\\textstylepagenumber",
		    "\\textstyleCharChar", 
		    "\\textstyleInternetlink",
		    "\\textstylefootnotereference",
		    "\\textstyleFootnoteTextChar",
		    "\\textstylepagenumber",
		    "\\textstyleappleconvertedspace",
		    "\\pagestyle{Standard}",
		    "\\hline",
		    "\\begin{center}",
		    "\\end{center}",
		    "\\begin{styleStandard}",
		    "\\end{styleStandard}",
		    "\\begin{styleIllustration}",
		    "\\end{styleIllustration}",
		    "\\begin{styleTabelle}",
		    "\\end{styleTabelle}",
		    "\\begin{styleAbbildung}",
		    "\\end{styleAbbildung}",
		    "\\begin{styleTextbody}",
		    "\\end{styleTextbody}",
		    "\\hline",
		    "\\maketitle",
		    "\\textstyleAbsatzStandardschriftart{}",
		    "\\textstyleAbsatzStandardschriftart",
		    "[Warning: Image ignored] % Unhandled or unsupported graphics:"
		    ) 
	for old, new in explicitreplacements:
	    modtext = modtext.replace(old,new)
	    
	for y in yanks:
	    modtext = modtext.replace(y,'')
	#unescape w2l unicode
	#w2lunicodep = re.compile(r'(\[[0-9A-Ea-e]{3}\?\])')
	#for m in w2lunicodep.findall(modtext):
	#     modtext=modtext.replace(m,'\u0{}'.format(m[1:-2]).decode('unicode_escape'))
	#remove marked up white space
	modtext = re.sub("\\text(it|bf|sc)\{( *)\}","\\2",modtext)  
	
	#remove explicit counters. These are not usefull when from autoconversion 
	
	#remove explicit table widths
	modtext = re.sub("m\{-?[0-9.]+(in|cm)\}","l",modtext)  
	modtext = re.sub("l\|","l",modtext)
	modtext = re.sub("\|l","l",modtext)
	modtext = re.sub(r"\\fontsize\{.*?\}\\selectfont","",modtext)
    
	#remove stupid Open Office styles 
	modtext = re.sub(r"\\begin\{styleHeadingi}\n+(.*?)\n+\\end\{styleHeadingi\}","\\chapter{\\1}",modtext)
	modtext = re.sub("\\\\begin\\{styleHeadingii\\}\n+(.*?)\n+\\\\end\\{styleHeadingii\\}","\\section{\\1}",modtext)
	modtext = re.sub("\\\\begin\{styleHeadingiii\}\n+(.*?)\n+\\\\end\{styleHeadingiii}","\\subsubsection{\\1}",modtext)
	modtext = re.sub("\\\\begin\{styleHeadingiv\}\n+(.*?)\n+\\\\end\{styleHeadingiv}","\\subsubsection{\\1}",modtext)
    
	#remove explicit shorttitle for sections
	modtext = re.sub("\\\\(sub)*section(\[.*?\])\{(\\text[bfmd][bfmd])\?(.*)\}","\\\\1section{\\4}",modtext) 
	#                        several subs | options       formatting           title ||   subs      title
	#move explict section number to end of line and comment out
	modtext = re.sub("section\{([0-9\.]+ )(.*)","section{\2 %\1/",modtext)
	modtext = re.sub("section\[.*?\]","section",modtext)
	#                                 number    title         title number
	#table cells in one row
	modtext = re.sub("[\n ]*&[ \n]*",' & ',modtext)
	modtext = modtext.replace(r'\ &','\&')
	#collapse newlines
	modtext = re.sub("\n*\\\\\\\\\n*",'\\\\\\\\\n',modtext) 
	#bib
	modtext = re.sub("\(([A-Z][a-z]+) +et al\.  +([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citep[\\3]{\\1EtAl\\2}",modtext)
	modtext = re.sub("\(([A-Z][a-z]+) +([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citep[\\3]{\\1\\2}",modtext)
	modtext = re.sub("\(([A-Z][a-z]+) +et al\. +([12][0-9]{3}[a-z]?)\)","\\citep{\\1EtAl\\2}",modtext)
	modtext = re.sub("\(([A-Z][a-z]+) +([12][0-9]{3}[a-z]?)\)","\\citep{\\1\\2}",modtext)
	#citet
	modtext = re.sub("([A-Z][a-z]+) +et al. +\(([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citet[\\3]{\\1EtAl\\2}",modtext)
	modtext = re.sub("([A-Z][a-z]+) +\(([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citet[\\3]{\\1\\2}",modtext)
	modtext = re.sub("([A-Z][a-z]+) +et al. +\(([12][0-9]{3}[a-z]?)\)","\\citet{\\1EtAl\\2}",modtext)
	modtext = re.sub("([A-Z][a-z]+) +\(([12][0-9]{3}[a-z]?)\)","\\citet{\\1\\2}",modtext)
	#modtext = re.sub("([A-Z][a-z]+) +([12][0-9]{3}[a-z]?)","\\citet{\\1\\2}",modtext)i

	#examples
	modtext = modtext.replace("\n()", "\n\\ea \n \\gll \\\\\n   \\\\\n \\glt\n\\z\n\n")
	modtext = re.sub("\n\(([0-9]+)\)", """\n\ea%\\1
    \label{ex:\\1}
    \langinfo{lg}{fam}{src}\\\\newline
    \\\\gll\\\\newline
	\\\\newline
    \\\\glt
    \z

	""",modtext)
	modtext = re.sub("\\label\{(bkm:Ref[0-9]+)\}\(\)", """ea%\\1
    \label{\\1}
    \langinfo{lg}{fam}{src}\\\\newline
    \\\\gll \\\\newline  
	\\\\newline
    \\\\glt
    \z

    """,modtext)
    
	#subexamples
	modtext = modtext.replace("\n *a. ","\n% \\ea\n%\\gll \n%    \n%\\glt \n")
	modtext = modtext.replace("\n *b. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n")    
	modtext = modtext.replace("\n *c. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n")  
	modtext = modtext.replace("\n *d. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n") 
	modtext = modtext.replace(r"\newline",r"\\")


	modtext = re.sub("\n\\\\textit{Table ([0-9]+)[\.:] *(.*?)}\n","%%please move \\\\begin{table} just above \\\\begin{tabular}\n\\\\begin{table}\n\\caption{\\2}\n\\label{tab:\\1}\n\\end{table}",modtext)
	modtext = re.sub("Table ([0-9]+)","\\\\tabref{tab:\\1}",modtext) 
	modtext = re.sub("\nFigure ([0-9]+)[\.:] *(.*?)\n","\\\\begin{figure}\n\\caption{\\2}\n\\label{fig:\\1}\n\\end{figure}",modtext)
	modtext = re.sub("Figure ([0-9]+)","\\\\figref{fig:\\1}",modtext)
	modtext = re.sub("Section ([0-9\.]+)","\\\\sectref{sec:\\1}",modtext) 
	modtext = re.sub("\\\\(begin|end){minipage}.*?\n",'',modtext)
	modtext = re.sub("\\\\begin{figure}\[h\]",'\\\\begin{figure}',modtext)
	
	
	modtext = re.sub("(begin\{tabular\}[^\n]*)",r"""\1
\lsptoprule""",modtext) 
	modtext = re.sub(r"\\end{tabular}",r"""\lspbottomrule
\end{tabular}""",modtext) 

	modtext = re.sub("""listWWNum[ivxlc]+level[ivxlc]+""","itemize",modtext) 
	modtext = re.sub("""listL[ivxlc]+level[ivxlc]+""","itemize",modtext) 
	

	
	modtext = re.sub("""\n+\\z""","\\z",modtext) 
	modtext = re.sub("""\n\n+""","\n\n",modtext) 
	
	#for s in ('textit','textbf','textsc','texttt','emph'):
	  #i=1
	  #while i!=0:
	    #modtext,i = re.subn('\\%s\{([^\}]+) '%s,'\\%s{\\1} \\%s{'%(s,s),modtext) 
	modtext = re.sub("\\\\includegraphics\[.*?width=\\\\textwidth","%please move the includegraphics inside the {figure} environment\n%%\includegraphics[width=\\\\textwidth",modtext)
	
	modtext = re.sub("\\\\item *\n+",'\\item ',modtext)
	return modtext
	    
if __name__ == '__main__':
    fn = sys.argv[1]
    d = convert(fn)
    tx = d.text
    mt = d.modtext
    out1 = codecs.open("temporig", "w", "utf-8")
    out2 = codecs.open("temp", "w", "utf-8")
    out1.write(tx)
    out2.write(mt)
    out1.close()
    out2.close()
