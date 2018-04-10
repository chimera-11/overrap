# note that this file was almost copied from somewhere on the Internet

from collections import defaultdict
from collections import Counter
from random import random
import sys
import time
import datetime
import hangul_comp

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
    for _ in range(nletters):
        c = generate_letter(lm, history, order)
        history = history[-order:] + c
        out.append(c)
    return "".join(out)

ngram_order = int(sys.argv[2])
lm = train_char_lm(sys.argv[1], order=ngram_order)

timestr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
iter = int(sys.argv[3])
for i in range(1, iter + 1):
    with open('synth_%s_try_%d.txt' % (timestr, i), 'w', encoding='utf8') as myfile:
        myfile.write(hangul_comp.process_data(generate_text(lm, ngram_order)))