from pyramid.view import view_config  
from pyramid.response import Response
import pyramid.httpexceptions as exc
import os
import re
import uuid
from .lib.langsci import  convert
from .lib.sanitycheck import  LSPDir
import shutil

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'doc2tex'}
    
@view_config(route_name='sanitycheck', renderer='templates/sanitycheck.pt')
def sanitycheck(request):   
    fn = request.POST['texbibzip'].filename 
    input_file = request.POST['texbibzip'].file
    filename = _upload(fn, input_file,('tex', 'bib', 'zip')) 
    filetype = filename.split('.')[-1]
    d = os.path.dirname(os.path.realpath(filename))
    lspdir = LSPDir(d)
    lspdir.check()   
    shutil.rmtree(d)
    return {'project': 'doc2tex',
	    'files':lspdir.errors}
  
    
def _upload(filename,f,accept):
    inputfn = filename
    input_file = f
    filetype = inputfn.split('.')[-1]
    if filetype not in accept:
	raise WrongFileFormatError(filetype)
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
    filename = _upload(filename, f,('doc', 'docx', 'odt'))
    #convert file to tex
    try:
	texdocument = convert(filename)
    except ValueError:
	raise FileFormatFailure(filetype)
    os.remove(filename)
    texdocument.ziptex()    
    texttpl = (('raw',texdocument.text),
	       ('mod',texdocument.modtext)
	      )
    return {'project': 'doc2tex',
	    'filename': inputfn,
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
    filetype = exc.args[0] if exc.args else ""
    msg =  'Files of type %s are not accepted. The only file types accepted are docx, doc, and odt' %filetype
    return {'project': 'doc2tex',
	    'msg': msg }
	    
