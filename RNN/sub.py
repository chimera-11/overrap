# -*- coding: utf-8 -*-

import codecs
import re

def read_data(filename):
    with codecs.open(filename, encoding='utf-8', mode='r') as f:
        data = f.read()
    return data

def delete_alpha(string) :
    result = re.sub('[^ \u3131-\u3163\uac00-\ud7a3\\n]+', '', string)
    return result

i = 1
data = ' '
while i < 392 :
    if i<10 :
        data = data + read_data('allcorpus/corpus ('+chr(ord('0')+i)+').txt')
    else :
        if 10<=i & i<100 :
            data = data + read_data('allcorpus/corpus ('+chr(ord('0')+(int)(i/10))+chr(ord('0')+i%10)+').txt')
        else:
            data = data + read_data('allcorpus/corpus ('+chr(ord('0')+(int)(i/100))+chr(ord('0')+(int)((i%100)/10))+chr(ord('0')+i%10)+').txt')
    i+=1
    
after_data = delete_alpha(data)
    
    
with codecs.open('input.txt', encoding='utf-8', mode='w') as f:
    f.write(after_data)