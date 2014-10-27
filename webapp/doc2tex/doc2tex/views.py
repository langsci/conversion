from pyramid.view import view_config
import os
import re
import uuid

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'doc2tex'}
    
    

@view_config(route_name='result', renderer='templates/result.pt')
def result(request): 
    inputfn = request.POST['docfile'].filename
    input_file = request.POST['docfile'].file
    
    file_path = os.path.join('/tmp', '%s.docx' % uuid.uuid4())

    print file_path
    # We first write to a temporary file to prevent incomplete files from
    # being used.

    temp_file_path = file_path + '~'
    output_file = open(temp_file_path, 'wb')

    # Finally write the data to a temporary file
    input_file.seek(0)
    while True:
        data = input_file.read(2<<16)
        if not data:
            break
        output_file.write(data)  
        
    output_file.close()

    # Now that we know the file has been fully saved to disk move it into place.

    os.rename(temp_file_path, file_path)
        
    #f = request.matchdict.get("docfile") 
    filename = file_path
    raw, mod = convert(filename)
    texttpl = (('raw',raw),
	    ('mod',mod)
	    )
    return {'project': 'doc2tex',
	    'filename': inputfn,
	    'texttpl': texttpl}
	    
def convert(fn):
    odtfn = False
    os.chdir('/home/doc2tex')
    if fn.endswith("docx"):
	odtfn = fn.replace("docx","odt").split('/')[-1]  
	syscall = """soffice --headless --convert-to odt "%s"  """ %fn
	print syscall
	os.system(syscall)
    if fn.endswith("doc"):
	odtfn = fn.replace("doc","odt")
	syscall = """soffice --headless --convert-to odt "%s"  """ %fn
	print syscall
	os.system(syscall)
    if fn.endswith("odt"):
	odtfn = fn.replace("docx","odt").split('/')[-1]  
    if odtfn == False:
	return False
    texfn = odtfn.replace("odt","tex")
    w2loptions = ("-clean",
    "-wrap_lines_after=0",
    "-multilingual=false", 
    #floats
    "-simple_table_limit=10"
    "-use_supertabular=false",
    "-float_tables=true", 
    "-float_figures=true", 
    "-use_caption=true", 
    '-image_options="width=\\textwidth"',
    #input
    "-inputencoding=utf8",
    "-use_tipa=false", 
    "-use_bibtex=true", 
    "-ignore_empty_paragraphs=true",
    #"-ignore_double_spaces=true", 
    #formatting
    "-formatting=convert_most",
    "-use_color=false",
    "-page_formatting=ignore_all",
    "-use_hyperref=true"
    )
    os.system("w2l {} {} {}".format(" ".join(w2loptions), odtfn, texfn))
    w2lcontent = open(texfn).read().decode('utf8')
    preamble, text = w2lcontent.split(r"\begin{document}")
    text = text.split(r"\end{document}")[0]
    preamble = '\n'.join([l for l in preamble.split() if "geometry" not in l and (l.startswith(r"\documentclass") or l.startswith(r"\usepackage") or l.startswith(r"\newcommand\text") or l.startswith(r"\newcounter"))])
    modtext = text
    explicitreplacements = (("{\\textquoteleft}","`"),
			    ("{\\textquotedblleft}","``"), 
			    ("{\\textquoteright}","'"),
			    ("{\\textquotedblright}","''"),
			    ("{\\textquotesingle}","'"),
			    ("{\\textquotedouble}",'"'),
			    ("\\textstyleVernacularWord","\\emph"),
			    ("\\textstyleGloss","\\textsc"),
			    ("\\par}","}"),
			    ("\\clearpage","\n"),
			    ("\\begin","\n\\begin"),
			    ("\\end","\n\\end"),
			    ("\ "," "),
                            ("supertabular","tabular"),
                            ("\\begin{center}","\\begin{table}\\centering"),
                            ("\\end{center}","\\caption{}\n%\\label{}\n\\end{table}\n"),
                            (" }","} ")
			)    
    yanks =  ( ("\\begin{flushleft}","\\end{flushleft}","\\centering","\\tablehead{}","\\textstylefootnotereference","\\textstylepagenumber","\\textstyleCharChar","\\textstyleIPA","\\textstyleInternetlink","\\textstylefootnotereference","\\textstyleFootnoteTextChar","\\textstylepagenumber","\\textstyleappleconvertedspace","\\pagestyle{Standard}","\-","\\hline")
			)
    for old, new in explicitreplacements:
	modtext = modtext.replace(old,new)
	
    for y in yanks:
	modtext = modtext.replace(y,'')
    
    #remove marked up white space
    modtext = re.sub("\\text(it|bf|sc)\{( *)\}","\\2",modtext)  
    
    #remove explicit table widths
    modtext = re.sub("m\{-?[0-9.]+in\}","l",modtext)  
    modtext = re.sub("l\|","l",modtext)
    modtext = re.sub("\|l","l",modtext)
 
    #remove explicit shorttitle for sections
    modtext = re.sub("\\\\(sub)*section(\[.*?\])\{(\\text[bfmd][bfmd])\?(.*)\}","\\\\1section{\\4}",modtext) 
    #                        several subs | options       formatting           title ||   subs      title
    #move explict section number to end of line and comment out
    modtext = re.sub("section\{([0-9\.]+ )(.*)","section{\2 %\1/",modtext)
    modtext = re.sub("section\[.*?\]","section",modtext)
    #                                 number    title         title number
    modtext = re.sub("[\n ]*&[ \n]*",' & ',modtext)
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

    #excamples
    modtext = modtext.replace("\n()", "\n\\ea \n \\gll \\\\\n   \\\\\n \\glt\n\\z\n\n")
    modtext = re.sub("\n\(([0-9]+)\)", """\n\ea%\\1
\label{ex:\\1}
\langinfo{}{}\\\\newline
\\\\gll\\\\newline
       \\\\newline
\\\\glt
\z

""",modtext)
    modtext = re.sub("\\label\{(bkm:Ref[0-9]+)\}\(\)", """ea%\\1
\label{\\1}
\langinfo{}{}\\\\newline
\\\\gll \\\\newline  
    \\\\newline
\\\\glt
\z

""",modtext)
    modtext = modtext.replace("\n *a. ","\n% \\ea\n%\\gll \n%    \n%\\glt \n")
    modtext = modtext.replace("\n *b. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n")    
    modtext = modtext.replace("\n *c. ","%\\ex\n%\\gll \\\\\n%    \\\\\n%\\glt \n%\\z\n")
    modtext = modtext.replace("\n *d. ",r"""
\ea
\gll \\
     \\
\glt 
\z
""")
    modtext = modtext.replace(r"\newline",r"\\")
    modtext = modtext.replace(r'\ &','\&')


    modtext = re.sub("Table ([0-9]+)[\.:](.*?)\n","\\\\begin{table}\n\\caption{\\2}\n\\label{tab:\\1}\n\\end{table}",modtext)
    modtext = re.sub("Table ([0-9]+)","\\tabref{tab:\\1}",modtext)
    modtext = re.sub("Figure ([0-9]+)[\.:](.*?)\n","\\\\begin{figure}\n\\caption{\\2}\n\\label{tab:\\1}\n\\end{figure}",modtext)
    modtext = re.sub("Figure ([0-9]+)","\\figref{fig:\\1}",modtext)
    modtext = re.sub("Section ([0-9\.]+)","\\sectref{sec:\\1}",modtext)


    
    w2lcontent = "\n".join((preamble, r"\usepackage[authoryear]{natbib}",r"\bibpunct[:]{(}{)}{,}{a}{}{,}",r"\begin{document}", text,"\\end{document}"))
    w2lmodcontent = "\n".join((preamble, r"\usepackage[authoryear]{natbib}",r"\bibpunct[:]{(}{)}{,}{a}{}{,}", r"\begin{document}", modtext,"\\end{document}"))
    return w2lcontent, w2lmodcontent
	    
	    
	    
#sanity 
# install
