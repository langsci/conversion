from pyramid.view import view_config
import os
import re
import uuid
from .lib.langsci import  convert

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def home(request):
    return {'project': 'doc2tex'}
    
    

@view_config(route_name='result', renderer='templates/result.pt')
def result(request): 
 
    inputfn = request.POST['docfile'].filename
    input_file = request.POST['docfile'].file
    filetype = inputfn.split('.')[-1]
    file_path = os.path.join('/tmp', '%s.%s' % (uuid.uuid4(),filetype))

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
    texdocument = convert(filename)
    texdocument.ziptex()
    
    texttpl = (('raw',raw),
	    ('mod',mod)
	    )
    return {'project': 'doc2tex',
	    'filename': inputfn,
	    'texttpl': texttpl}
	    
	    
	    
	    
#sanity 
# install
