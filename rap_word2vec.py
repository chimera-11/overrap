# -*- coding: utf-8 -*-

import gensim
import random

def load_word2vec_model(path):
    model = gensim.models.word2vec.Word2Vec()
    return model.wv.load(path)

class RapWord2Vec:
    def __init__(self, scope=30, minus=0.1):
        self.scope = scope
        self.minus = minus
        self.model_1 = load_word2vec_model('model_word2vec\\model_1')
        self.model_2 = load_word2vec_model('model_word2vec\\model_2')
        self.model_c = load_word2vec_model('model_word2vec\\model_c')
    def sum_similar(self, f, t):
        tf = True
        for x in f:
            if x[1] == t[0] :
                x[0] += t[1]
                tf = False
                break
        if tf :
            f.append([t[1], t[0]])
        return f
    def minus_counter(self, f, t):
        tf = True
        for x in f:
            if x[1] == t[0]:
                x[0] -= t[1] * self.minus
                tf = False
                break
        if tf:
            f.append( [(-1) * self.minus * t[1], t[0]])
        return f
    def choose_word(self, word, scope=None):
        if scope is None:
            scope = self.scope
        rank = []
        if(self.is_vocab(word, self.model_1)) :
            for x in self.model_1.most_similar(word) :
                rank = self.sum_similar(rank, x)
        if(self.is_vocab(word, self.model_2)) :
            for y in self.model_2.most_similar(word) :
                rank = self.sum_similar(rank, y)
        if(self.is_vocab(word, self.model_c)) :
            for z in self.model_c.most_similar(word) :
                rank = self.minus_counter(rank, z)
        rank.sort(reverse = True)
        select = rank[0:scope]
        #return select
        return select[random.randint(0, len(select)-1)][1]
        #random sampling
        
    def choose_word_set(self, word, scope=None):
        if scope is None:
            scope = self.scope
        rank = []
        if(self.is_vocab(word, self.model_1)) :
            for x in self.model_1.most_similar(word) :
                rank = self.sum_similar(rank, x)
        if(self.is_vocab(word, self.model_2)) :
            for y in self.model_2.most_similar(word) :
                rank = self.sum_similar(rank, y)
        if(self.is_vocab(word, self.model_c)) :
            for z in self.model_c.most_similar(word) :
                rank = self.minus_counter(rank, z)
        rank.sort(reverse = True)
        select = rank[0:scope]
        return select

    def choose_word_exclude_nonrhyme(self, b, d, scope):
        rank = []
        if(self.is_vocab(b, self.model_1)) :
            for x in self.model_1.most_similar(b) :
                rank = self.sum_similar(rank, x)
        if(self.is_vocab(b, self.model_2)) :
            for y in self.model_2.most_similar(b) :
                rank = self.sum_similar(rank, y)
        if(self.is_vocab(b, self.model_c)) :
            for z in self.model_c.most_similar(b) :
                rank = self.minus_counter(rank, z)
        if(self.is_vocab(d, self.model_1)) :
            for x in self.model_1.most_similar(d) :
                rank = self.sum_similar(rank, x)
        if(self.is_vocab(d, self.model_2)) :
            for y in self.model_2.most_similar(d) :
                rank = self.sum_similar(rank, y)
        if(self.is_vocab(d, self.model_c)) :
            for z in self.model_c.most_similar(d) :
                rank = self.minus_counter(rank, z)
        rank.sort(reverse = True)
        select = rank[0:scope]
        #return select
        return select[random.randint(0, len(select)-1)][1]

    def random_vocab(self):
        vocab = []
        for x in self.model_1.wv.vocab :
            if (x[len(x)-1] == 'n') & (x[len(x)-2] == 'u') :
                vocab.append(x)
        return vocab[random.randint(0, len(vocab)-1)]

    def generate_words(self, a, b, scope=None):
        if scope is None:
            scope = self.scope
        if (a==' ') & (b==' ') :
            c = self.random_vocab()
            d = self.choose_word(c, scope)
            return c, d
        else:
            c = self.choose_word(a, scope)
            d = self.choose_word_exclude_nonrhyme(b, c, scope)
            return c, d
    def is_vocab(self, word, model):
        for x in model.wv.vocab :
            if x == word :
                return True
        return False

if __name__ == '__main__':
    rw2v = RapWord2Vec()
    num = ' '
    while num != '-1' :
        num = input("Input a number 1) to get 1 word with information\n2) to get\na b\nc d\ne f\ng h\nstyle random sampling\n or -1\n")
        if num == '-1' :
            break
        elif num == '1' :
            word = input("Input a word which want to get a info\n")
            if rw2v.is_vocab(word, rw2v.model_1) | rw2v.is_vocab(word, rw2v.model_2) :
                print("result : \n")
                print(rw2v.choose_word_set(word))
            else:
                print("the word isn't in the vocabulary\n")
        elif num == '2' :
            (a,b) = rw2v.generate_words(' ', ' ')
            (c,d) = rw2v.generate_words(a, b)
            (e,f) = rw2v.generate_words(c, d)
            (g,h) = rw2v.generate_words(e, f)
            print(a,b+"\n"+c,d+"\n"+e,f+"\n"+g,h)