#!/bin/sh

# This converter converts an odt document to a tex document, 
# The output can then be pdftexed.
# The script does not work on doc(x), so you have to first use OpenOffice or MS-Word and save the file as odt

w2l -clean -wrap_lines_after=0 -multilingual=false -float_table=true -float_figure=true -use_caption=true -image_options="width=\textwidth" -use_tipa=true -use_bibtex=true -ignore_double_spaces=true -multilingual=false -formatting=ignore_most -use_color=false $1