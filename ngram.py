# note that this file was almost copied from somewhere on the Internet

from collections import defaultdict
from collections import Counter
from random import random
import sys
import time
import datetime
import hangul
import hangul_comp

class Ngram:
    def train_char_lm(self, fname, order=4):
        self.order = order
        with open(fname, 'r', encoding='utf8') as myfile:
            data = myfile.read()
        lm = defaultdict(Counter)
        #pad = "~" * order
        #data = pad + data
        for suborder in range(2, order+1):
            for i in range(len(data) - suborder):
                history, char = "~" * (order - suborder) + data[i : i + suborder], data[i + suborder]
                lm[history][char]+=1
        def normalize(counter):
            s = float(sum(counter.values()))
            return [(c,cnt/s) for c,cnt in counter.items()]
        outlm = {hist:normalize(chars) for hist, chars in lm.items()}
        self.lm = outlm
        return outlm

    def generate_letter(self, history, order):
        history = history[-order:]
        dist = self.lm[history]
        x = random()
        for c,v in dist:
            x = x - v
            if x <= 0: return c

    def generate_text(self, order, start_str='', nletters=1000):
        history = "~" * order
        for c in start_str:
            history = history[-order:] + c
        output_str = ''
        while not hangul.is_complete(output_str) or len(hangul_comp.process_data(output_str)) < nletters:
            c = self.generate_letter(history, order)
            history = history[-order:] + c
            output_str += c
            #print(hangul_comp.process_data(output_str))
        return output_str

if __name__ == '__main__':
    input_source = sys.argv[1]
    ngram_order = int(sys.argv[2])
    ngram = Ngram()
    ngram.train_char_lm(sys.argv[1], order=ngram_order)

    timestr = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d-%H%M%S')
    iter = int(sys.argv[3])
    for i in range(1, iter + 1):
        with open('synth_%s_try_%d.txt' % (timestr, i), 'w', encoding='utf8') as myfile:
            myfile.write(hangul_comp.process_data(ngram.generate_text(ngram_order)))