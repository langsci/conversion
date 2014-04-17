#!/bin/sh
# usage ./doc2tex.sh file.doc
 

# echo $1
docfile=$1 
odtfile="`basename $docfile .docx`.odt"
textmpfile="`basename $docfile .docx`tmp.tex"
texfile="`basename $docfile .docx`.tex"
pdffile="`basename $docfile .docx`.pdf"
 

echo "converting doc to odt"
soffice --headless --convert-to odt $docfile

echo "converting odt to tex"
w2l -clean -wrap_lines_after=0 -multilingual=false -float_table=true -float_figure=true -use_caption=true -image_options="width=\textwidth" -use_tipa=true -use_bibtex=true -ignore_double_spaces=true -multilingual=false -formatting=ignore_most -use_color=false $odtfile $textmpfile

echo "replacing stupid formatting decisions by w2l"
sed -f odttex2truetex.sed $textmpfile>$texfile

echo "create pdf"
pdflatex $texfile
pdflatex $texfile

echo "show pdf file"
okular $pdffile


