from pyramid.view import view_config
import os
import re
import uuid

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'doc2tex'}
    
    

@view_config(route_name='result', renderer='templates/result.pt')
def result(request): 
    #fn = request.POST['docfile'].filename
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
	    'filename': 'test.docx',
	    'texttpl': texttpl}
	    
def convert(fn):
    odtfn = False
    if fn.endswith("docx"):
	odtfn = fn.replace("docx","odt").split('/')[-1]
	print odtfn
	os.system("""soffice --headless --convert-to odt "%s" """ %fn)
    if fn.endswith("doc"):
	odtfn = fn.replace("docx","odt")
	os.system("""soffice --headless --convert-to odt "%s" """ %fn)
    if fn.endswith("odt"):
	odtfn = fn
    if odtfn == False:
	return False
    texfn = odtfn.replace("odt","tex")
    w2loptions = ("-clean",
    "-wrap_lines_after=0",
    "-multilingual=false", 
    "-float_table=true", 
    "-float_figure=true", 
    "-use_caption=true", 
    '-image_options="width=\\textwidth"',
    "-use_tipa=true", 
    "-use_bibtex=true", 
    "-ignore_double_spaces=true", 
    "-multilingual=false", 
    "-formatting=ignore_most",
    "-use_color=false")
    os.system("w2l {} {} {}".format(" ".join(w2loptions), odtfn, texfn))
    w2lcontent = open(texfn).read()
    preamble, text = w2lcontent.split(r"\begin{document}")
    text = text.split(r"\end{document}")[0]
    preamble = '\n'.join([l for l in preamble.split() if "geometry" not in l and (l.startswith(r"\documentclass") or l.startswith(r"\usepackage"))])
    modtext = text
    explicitreplacements = (("{\\textquoteleft}","`"),
			    ("{\\textquotedblleft}","``"), 
			    ("{\\textquoteright}","'"),
			    ("{\\textquotesingle}","'"),
			    ("{\\textquotedblright}","''"),
			    ("\\textstyleVernacularWord","\\emph"),
			    ("\\textstyleGloss","\\textsc"),
			    ("\\par}","}"),
			    ("\\clearpage","\n"),
			    ("\\begin","\n\\begin"),
			    ("\\end","\n\\end"),
			)    
    yanks =  ( ("\\begin{flushleft}","\\end{flushleft}","\\centering","\\tablehead{}","\\textstylefootnotereference","\\textstylepagenumber","\\textstyleCharChar","\\textstyleIPA","\\textstyleInternetlink","\\textstylefootnotereference","\\textstyleFootnoteTextChar","\\textstylepagenumber","\\textstyleappleconvertedspace","\\pagestyle{Standard}")
			)
    for old, new in explicitreplacements:
	modtext = modtext.replace(old,new)
	
    for y in yanks:
	modtext = modtext.replace(y,'')
    
    #remove marked up white space
    modtext = re.sub("\\text(it|bf|sc)\{( *)\}","\\2",modtext)  
    
    #remove explicit table widths
    modtext = re.sub("m\{-?[0-9.]+in\}","l",modtext)  
    
    #remove explicit shorttitle for sections
    modtext = re.sub("\\\\(sub)*section(\[.*?\])\{(\\text[bfmd][bfmd])\?(.*)\}","\\\\1section{\\4}",modtext) 
    #                        several subs | options       formatting           title ||   subs      title
    #move explict section number to end of line and comment out
    modtext = re.sub("section\{([0-9\.]+ )(.*)","section{\2 %\1/",modtext)
    #                                 number    title         title number
    
    #bib
    modtext = re.sub("\(([A-Z][a-z]+) +([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citep[\\3]{\\1\\2}",modtext)
    modtext = re.sub("([A-Z][a-z]+) +\(([12][0-9]{3}[a-z]?): *([0-9,-]+)\)","\\citet[\\3]{\\1\\2}",modtext)
    modtext = re.sub("\(([A-Z][a-z]+) +([12][0-9]{3}[a-z]?)\)","\\citep{\\1\\2}",modtext)
    modtext = re.sub("([A-Z][a-z]+) +\(([12][0-9]{3}[a-z]?)\)","\\citet{\\1\\2}",modtext)
    modtext = re.sub("([A-Z][a-z]+) +([12][0-9]{3}[a-z]?)","\\citet{\\1\\2}",modtext)
    
    w2lcontent = "\n".join((preamble, r"\usepackage[authoryear]{natbib}",r"\bibpunct[:]{(}{)}{,}{a}{}{,}",r"\begin{document}", text,"\\end{document}"))
    w2lmodcontent = "\n".join((preamble, r"\usepackage[authoryear]{natbib}",r"\bibpunct[:]{(}{)}{,}{a}{}{,}", r"\begin{document}", modtext,"\\end{document}"))
    return w2lcontent, w2lmodcontent
	    
	    
	    
#sanity 
# install
