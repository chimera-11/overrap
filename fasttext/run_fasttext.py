import random
from gensim.models import KeyedVectors

file_path = 'wiki.ko.vec'

scope = 50

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
    for x in model.most_similar(word, topn=1000) :
        rank = sum_similar(rank, x)
    rank.sort(reverse = True)
    select = rank[0:scope]
    return select[random.randint(0, len(select)-1)][1]
    
def choosing_word_set(word, scope):
    rank = []
    for x in model.most_similar(word, topn=1000) :
        rank = sum_similar(rank, x)

    rank.sort(reverse = True)
    select = rank[0:scope]
    return select

def double_choosing_word(b, d, scope):
    rank = []
    for x in model.most_similar(b, topn=1000) :
        rank = sum_similar(rank, x)
    for y in model.most_similar(d, topn=1000) :
        rank = sum_similar(rank, y)

    rank.sort(reverse = True)
    select = rank[0:scope]
    return select[random.randint(0, len(select)-1)][1]


def generating_words(a, b, scope):
    if (a==' ') & (b==' ') :
        c = random_vocab()
        d = choosing_word(c, scope)
        return c, d
    else:
        c = choosing_word(a, scope)
        d = double_choosing_word(b, c, scope)
        return c, d
    
def random_vocab():
    return vocab[random.randint(0, len(vocab)-1)]


model = KeyedVectors.load_word2vec_format(file_path)

vocab = model.index2word

#model.most_similar('영화', topn=100)


num = ' '
while num != '-1' :
    num = input("Input a number 1) to get 1 word with information\n2) to get\na b\nc d\nstyle random sampling\n or -1\n")
    if num == '-1' :
        break
    elif num == '1' :
        word = input("Input a word which want to get a info\n")
        print("result : \n")
        print(choosing_word_set(word, scope))
    elif num == '2' :
        (a,b) = generating_words(' ', ' ', scope)
        (c,d) = generating_words(a, b, scope)
        print(a,b+"\n"+c,d)