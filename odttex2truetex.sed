# use this for manual replacement of suboptimal w2l output in kate. Will eventually be converted into a sed script
# the upper line in a group is the target, the lower line the replacement

#replace verbose renderings of normal quotation marks
s/{\\textquoteleft}/`/g
s/{\\textquotedblleft}/``/g
s/{\\textquoteright}/'/g
s/{\\textquotesingle}/'/g
s/{\\textquotedblright}/''/g

#add a couple of newlines for legibility
s/\\clearpage/\n/g
s/\\begin/\n\\begin/g
s/\\end/\n\\end/g

#undo explicit flushleft
s/\\begin{flushleft}//
s/\\end{flushleft}//

#undo centering
#(useless in 99% of the time)
s/\\centering//

#undo hard spaces
s/\(\\ \)\+/ /g

#remove empty elements
s/\\tablehead{}//
s/\\par}/}/

#remove markup of white space
s/\\textit{\( *\)}/\1/
s/\\textbf{\( *\)}/\1/
s/\\textsc{\( *\)}/\1/

#undo explicit table widths
s/m{-\?[0-9\.]\+in}/l/g
#move columns together

#remove explicit shorttitle for sections
s/\\\(sub\)*section\(\[[^\]*\]\)\?{\(\\text[bfmd][bfmd]\)\?\(.*\)}/\\\1section{\4}/
#move explict section number to end of line and comment out
s/section{\([0-9\.]\+ \)\(.*\)/section{\2 %\1/

# #put example labels where they belong
# s/\\label{\(bkm:Ref.*\)}/\\ea\\label{\1}\n\\z\n/
# 
# #find examples and use gb4e to render them
# s/^(\([0-9]\{,3\}\)) \(.*\)/\\ea%\1\n\\gll \2\\\\\n\\\\\n\\z /
# 
# #undo explicit italicizing of first line of example
# s/\\gll *\\textit{\(.*\)} *\\/\\gll \1 /

#refs
s/(\([A-Z][a-z]\+\) \+\([12][0-9]\{3\}[a-z]\?\): *\([0-9,-]\+\))/\\citep[\3]{\1\2}/g
s/(\([A-Z][a-z]\+\) \+\([12][0-9]\{3\}[a-z]\?\))/\\citep{\1\2}/g
s/\([A-Z][a-z]\+\) \+(\([12][0-9]\{3\}[a-z]\?\))/\\citet{\1\2}/g
s/\([A-Z][a-z]\+\) \+\([12][0-9]\{3\}[a-z]\?\)/\\citet{\1\2}/g
