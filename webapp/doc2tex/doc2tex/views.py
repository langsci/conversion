from pyramid.view import view_config  
from pyramid.response import Response
import pyramid.httpexceptions as exc
import os
import re
import uuid
from .lib.langsci import  convert
from .lib.sanitycheck import  LSPDir
from .lib.normalizebib import  normalize
from .lib import  sanityoverleaf
import shutil
import string
from lib import langscibibtex

@view_config(route_name='doc2tex', renderer='templates/mytemplate.pt')
def doc2tex(request):
  return {'project': 'doc2tex'}

  
@view_config(route_name='doc2bib', renderer='templates/doc2bib.pt')
def dco2bib(request): 
        biboutput = ''
        try:
                bibinput = request.POST['bibinput'].strip()
                biboutput = '\n\n'.join([langscibibtex.Record(l).bibstring for l in bibinput.split('\n')])
                #biboutput = '\n'.join([str(len(l)) for l in bibinput.split('\n')])
        except KeyError:
                #bibinput = "Paste your bibliography here" 
                bibinput = """Bloomfield, Leonard. 1925. On the sound-system of central Algonquian. Language 1(4). 130-156.

Lahiri, Aditi (ed.). 2000. Analogy, leveling, markedness: Principles of change in phonology and morphology (Trends in Linguistics 127). Berlin: Mouton de Gruyter.
""" 
        return {'project': 'doc2bib',
        'bibinput': bibinput,
        'biboutput': biboutput
                                }
    
    
@view_config(route_name='normalizebib', renderer='templates/normalizebib.pt')
def normalizebib(request): 
        biboutput = ''
        try:
                bibinput = request.POST['bibinput'].strip()
                biboutput = normalize(bibinput)
        except KeyError:
                bibinput = """
%This is a comment

@article{Jones1999,
  author = {Jane Jones et al},
  year = {1999},
  title = {Exploring unknown movements of NP},
  journal = {Annals of Improbable research}
}

@BOOK{Smith2000,
  author = {John Smith},
  year = {2000},
  title = {A Grammar of the Turkish Language},
  publisher = {Oxford University Press}
}
"""
        #biboutput = bibinput
        return {'project': 'normalizebib',
        'bibinput': bibinput,
        'biboutput': biboutput
                                }
    
@view_config(route_name='sanitycheck', renderer='templates/sanitycheck.pt')
def sanitycheck(request):   
    fn = request.POST['texbibzip'].filename 
    input_file = request.POST['texbibzip'].file
    filename = _upload(fn, input_file,('tex', 'bib')) 
    filetype = filename.split('.')[-1]
    d = os.path.dirname(os.path.realpath(filename))
    lspdir = LSPDir(d)
    lspdir.check()  
    #shutil.rmtree(d)
    return {'project': 'doc2tex',
            'files':lspdir.errors,
            'imgs':[]}
  
@view_config(route_name='overleafsanity', renderer='templates/sanitycheck.pt')
def overleafsanity(request):   
    overleafurl = request.GET['overleafurl']
    d = sanityoverleaf.cloneorpull(overleafurl)
    lspdir = LSPDir(os.path.join(d,"chapters"))
    lspdir.check()
    imgdir = LSPDir(os.path.join(d,"figures"))
    imgdir.check()
    #shutil.rmtree(d)
    return {'project': 'doc2tex',
            'files':lspdir.errors,
            'imgs':imgdir.errors}
  
    
def _upload(filename,f,accept):
    inputfn = ''.join([c for c in filename if c in string.ascii_letters or c in string.digits or c =='.'])
    input_file = f
    filetype = inputfn.split('.')[-1]
    if filetype not in accept:
        raise WrongFileFormatError(filetype,accept)
    tmpdir = '%s'%uuid.uuid4()
    os.mkdir(os.path.join('/tmp',tmpdir))
    #tmpfile = '%s.%s' % (uuid.uuid4(),filetype)
    file_path = os.path.join('/tmp',tmpdir,inputfn)
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
    return file_path
      

@view_config(route_name='result', renderer='templates/result.pt')
def result(request):  
    fn = request.POST['docfile'].filename
    input_file = request.POST['docfile'].file
    filename = _upload(fn, input_file,('doc', 'docx', 'odt'))
    #convert file to tex
    try:
        texdocument = convert(filename)
    except ValueError:
        raise FileFormatFailure(filetype)
    except IOError:
        raise Writer2LatexError 
    #os.remove(filename)
    texdocument.ziptex()    
    texttpl = (('raw',texdocument.text),
               ('mod',texdocument.modtext)
              )
    return {'project': 'doc2tex',
            'filename': fn,
            'texttpl': texttpl, 
            'zipurl': "http://www.glottotopia.org/wlport/%s.zip"%texdocument.zipfn}
            

class FileFormatFailure(Exception):
    pass

@view_config(context=FileFormatFailure, renderer='templates/error.pt')
def failed_conversion(exc, request):
    # If the view has two formal arguments, the first is the context.
    # The context is always available as ``request.context`` too.
    filetype = exc.args[0] if exc.args else ""
    response =  Response('Failed conversion: file of type %s could not be converted. A common cause is a table of contents or other automated index. Remove this from your file, save, and try again.' %filetype)
    response.status_int = 500
    return response
    
class WrongFileFormatError(Exception):
    pass

@view_config(context=WrongFileFormatError, renderer='templates/error.pt')
def wrongfileformat(exc, request):
    # If the view has two formal arguments, the first is the context.
    # The context is always available as ``request.context`` too.
    filetype,accept = exc.args[0] if exc.args else "",""
    msg =  'Files of type %s are not accepted. The only file types accepted are %s' % (filetype, ", ".join(accept))
    return {'project': 'doc2tex',
            'msg': msg }
            
             
class Writer2LatexError(Exception):
    pass

@view_config(context=Writer2LatexError, renderer='templates/error.pt')
def w2lerror(exc, request):
    # If the view has two formal arguments, the first is the context.
    # The context is always available as ``request.context`` too.
    filetype = exc.args[0] if exc.args else ""
    msg =  """The file could not be converted. Common causes are:
                 1. file format. *odt is best, *doc is also possible, *docx is the most problematic format 
                 2. an automatic table of contents
                 3. many graphics 
                 4. complicated tables. Remove problematic elements from your file, save in another format and retry.
    """ 
    return {'project': 'doc2tex',
            'msg': msg }
            
