# -*- coding: utf-8 -*-

import gensim
import random

scope = 30

def sum_similar(f, t):
    tf = True
    for x in f:
        if x[1] == t[0] :
            x[0] += t[1]
            tf = False
            break
    if tf :
        f.append([t[1], t[0]])
    return f

def choosing_word(word, scope):
    rank = []
    if(isVocab(word, model_1)) :
        for x in model_1.most_similar(word) :
            rank = sum_similar(rank, x)
    rank.sort(reverse = True)
    select = rank[0:scope]
    return select[random.randint(0, len(select)-1)][1]

    
def choosing_word_set(word, scope):
    rank = []
    if(isVocab(word, model_1)) :
        for x in model_1.most_similar(word) :
            rank = sum_similar(rank, x)
    rank.sort(reverse = True)
    select = rank[0:scope]
    return select

def double_choosing_word(b, d, scope):
    rank = []
    if(isVocab(b, model_1)) :
        for x in model_1.most_similar(b) :
            rank = sum_similar(rank, x)
    if(isVocab(d, model_1)) :
        for x in model_1.most_similar(d) :
            rank = sum_similar(rank, x)
    rank.sort(reverse = True)
    select = rank[0:scope]
    return select[random.randint(0, len(select)-1)][1]

def random_vocab():
    vocab = []
    for x in model_1.vocab :
       # print(x)
       # if (x[len(x)-1] == 'n') & (x[len(x)-2] == 'u') :
        vocab.append(x)
    return vocab[random.randint(0, len(vocab)-1)]

def generating_words(a, b, scope):
    if (a==' ') & (b==' ') :
        c = random_vocab()
        d = choosing_word(c, scope)
        return c, d
    else:
        c = choosing_word(a, scope)
        d = double_choosing_word(b, c, scope)
        return c, d

def isVocab(word, model):
    for x in model.wv.vocab :
        if x == word :
            return True
    return False   

model_1 = gensim.models.word2vec.Word2Vec()
model_1 = model_1.wv.load('model_phrase_token')



num = ' '
while num != '-1' :
    num = input("Input a number 1) to get 1 word with information\n2) to get\na b\nc d\ne f\ng h\nstyle random sampling\n or -1\n")
    if num == '-1' :
        break
    elif num == '1' :
        word = input("Input a word which want to get a info\n")
        if isVocab(word, model_1) :
            print("result : \n")
            print(choosing_word_set(word, scope))
        else:
            print("the word isn't in the vocabulary\n")
    elif num == '2' :
        (a,b) = generating_words(' ', ' ', scope)
        (c,d) = generating_words(a, b, scope)
        (e,f) = generating_words(c, d, scope)
        (g,h) = generating_words(e, f, scope)
        print(a,b+"\n"+c,d+"\n"+e,f+"\n"+g,h)