# -*- coding: utf-8 -*-
import codecs
import re
from konlpy.tag import Twitter
tagger = Twitter()


def count_each_line(line, corpus) :
    i = 0
    j = 0
    count = 0
    while i < len(line) - 1 :
        j = i + 1
        while j < len(line) - 1 :
            count = count + count_each_pair(line[i], line[j], corpus)
            j = j + 1
        i = i + 1
    return count, (len(line) * (len(line) - 1) / 2)

def count_each_pair(x, y, corpus) :
    count = 0
    for line in corpus :
        count = count + count_line_to_line(x, y, line)
    return count
        
def count_line_to_line(x, y, line) :
    i = 0
    j = 0
    while i < len(line)-1 :
        if x == line[i] :
            j = i + 1
            while j < len(line) :
                if y == line[j] :
                    return 1
                j = j + 1
        elif y == line[i] :
            j = i + 1
            while j < len(line) :
                if y == line[j] :
                    return 1
                j = j + 1
        i = i + 1
    return 0

def count_corpus_pair(corpus) :
    count = 0
    for line in corpus :
        count = count + len(line) * (len(line) - 1) / 2
    return count

def tokenize(doc):
    return ['/'.join(t) for t in tagger.pos(doc, norm=True, stem=True)]

def read_data(filename):
    with codecs.open(filename, encoding='utf-8', mode='r') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        data = data[1:]   # header 제외
    return data

def delete_alpha(string) :
    hangul = re.compile('[^ \u3131-\u3163\uac00-\ud7a3\\n]+')
    result = []
    for x in string :
        result.append([hangul.sub('', x[0])])
    return result

path = 'example.txt'
c_path = 'corpus/corpus (1).txt'

temp = read_data(path)
corpus = read_data(c_path) #+ read_data('corpus/corpus (2).txt') + read_data('corpus/corpus (3).txt')

temp_1 = [row[0] for row in delete_alpha(temp)] 
corpus_1 = [row[0] for row in delete_alpha(corpus)] 
temp_2 = [tokenize(x) for x in temp_1]
corpus_2 = [tokenize(x) for x in corpus_1]

count = 0
every = 0

for line in temp_2:
    a,b = count_each_line(line, corpus_2)
    count = count + a
    every = every + b

print(count, every, count_corpus_pair(corpus_2))
print(count/every/count_corpus_pair(corpus_2) * 10000)

