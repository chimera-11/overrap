from collections import defaultdict
from collections import Counter
from random import random
import sys

def train_char_lm(fname, order=4):
    with open(fname, 'r', encoding='utf8') as myfile:
        data = myfile.read()
    lm = defaultdict(Counter)
    pad = "~" * order
    data = pad + data
    for i in range(len(data) - order):
        history, char = data[i : i + order], data[i + order]
        lm[history][char]+=1
    def normalize(counter):
        s = float(sum(counter.values()))
        return [(c,cnt/s) for c,cnt in counter.items()]
    outlm = {hist:normalize(chars) for hist, chars in lm.items()}
    return outlm

def generate_letter(lm, history, order):
    history = history[-order:]
    dist = lm[history]
    x = random()
    for c,v in dist:
        x = x - v
        if x <= 0: return c

def generate_text(lm, order, nletters=1000):
    history = "~" * order
    out = []
    for i in range(nletters):
        c = generate_letter(lm, history, order)
        history = history[-order:] + c
        out.append(c)
    return "".join(out)

ngram_order = int(sys.argv[2])
lm = train_char_lm(sys.argv[1], order=ngram_order)
print(generate_text(lm, ngram_order))