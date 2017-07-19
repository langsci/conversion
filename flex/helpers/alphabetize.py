import re

CITATIONFORM = re.compile('citationform\{(.*?)\}%')

AS = ('{\\higha}',
      'á',
      'à',
      'â',
      'Á',
      'À'
      )
ES = ('{\\highe}',
      'é','é','é',
      'è',
      'è','è','è',
      'ê',
      'ɛ́',
      'ɛ̀',
      'ɛ',
      'Ɛ́'
      '{\\highe}',
      '{\\highE}',
      'Ɛ́'
      )
IS = ('{\\highi}',
      '{\\I}',
      '{\\Í}',
      '{\\Ì}',
      '{\\Î}',
      '{\\i}',
      '{\\í}',
      '{\\ì}',
      '{\\î}',
      '{\\highi}',
      '{\\highI}',
      'ɨ',
      'í',
      'ì',
      'î',
      'Í',
      'Ì' 
      )
OS  = (
      '{\\higho}',
      '{\\highO}',
      'ó',
      'ó',
      'ò',
      'ô',
      'ɔ́',
      'ɔ́',
      'ɔ̀',
      'ɔ',
      '^ɔ',
      'Ɔ',
      'Ó',
      'Ò',
      'Ɔ́'
      )
US = (
      '{\\highu}',
      '{\\U}',
      '{\\Ú}',
      '{\\Ù}',
      '{\\Û}',
      '{\\highU}',
      'ú',
      'ù',
      'û',
      'ʉ́',
      'ʉ̀',
      'ʉ',
      'Ú'
      )
JS = (
      'ʝ',
      'ʝ' 
      )
NS = (
      'ń',
      'ǹ'
      )
NYS = (
      'ɲ',
      'Ɲ'
      )
NGS = (
      'ŋ',
      'Ŋ'
      )
DS = (
      'ɗ',
      'Ɗ' 
      )
HS = (
      'ɦ' 
      )
GS = (
      'ɡ' 
      )
BS = (
    'ɓ',
    'Ɓ'
    )
KS = (
    'ƙ',
    'Ƙ'
    )

NUMERICREPLACEMENTS=[(595, 98.5),#ɓ
                     (385, 98.5),#Ɓ
                     (599, 100.5),#ɗ
                     (394, 100.5),#Ɗ
                     (609, 103),#ɡ
                     (614, 104.5),#ɦ
                     (669, 106.5), #ʝj
                     (409, 107.5),#ƙ 
                     (408, 107.5),#Ƙ
                     (626, 110.3), #ɲ
                     (413, 110.3), #Ɲ
                     (331, 110.6),#ŋ
                     (330, 110.6), #Ŋ
                     ]


def conform(s): 
  for a in AS:
    s = s.replace(a, 'a')
  for e in ES:
    #print(e,s),
    s = s.replace(e, 'e')
    #print(s)
  for i in IS:
    s = s.replace(i, 'i')
  for o in OS:
    s = s.replace(o, 'o')
  for u in US:
    s = s.replace(u, 'u')  
  for n in NS:
    s = s.replace(n, 'n')  

#CONSONANTS
  s = s.lower()
  numeric = [ord(c) for c in s]
  result = [None for c in s]
  for i,number in enumerate(numeric):
    result[i] = number #standard case
    for old, new in NUMERICREPLACEMENTS:
      if number == old:
        result[i] = new #replacement case
        continue  
  return result

 

entries = open('chapters/dictionary.tex').read()\
  .split('%------------------------------')
entries = entries[1:] #strip first begin letter
keys = []
for e in entries:
  m = CITATIONFORM.search(e)
  if m:
    lexicalunit = m.group(1) 
    lexicalunit = conform(lexicalunit)
    keys.append(lexicalunit) 
    
z = list(zip(keys,entries))
z.sort()
output = '%------------------------------'.join(['\\begin{letter}{a}'] + [e[1] for e in z])
out = open('chapters/dictionary2.tex', 'w')
out.write(output)
out.close()

    