# decomposition of Hangul characters into two or three parts

import sys
import hangul

with open(sys.argv[1], 'r', encoding='utf8') as myfile:
    data = myfile.read()

processed_data = []
for c in data:
    if hangul.is_hangul_char(c):
        processed_data.append(hangul.decompose_hangul(c))
    else:
        processed_data.append(c)
    #input(processed_data)

with open(sys.argv[2], 'w', encoding='utf8') as myfile:
    myfile.write(''.join(processed_data))