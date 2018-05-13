# ---------------------------------------------
#   lyrics_gen.py
#   Copyright (C) 2018 Overrap Developers
# ---------------------------------------------
# Description:
#     This module generates lyrics lines
#     by the following procedure:
#       1> Generate pivot words from word2vec
#       2> Ligate them using RNN
#       3> Select lines with higher rhyme density
#       4> Re-arrange the relative position of lines
#          using rhyme density
# Usage:
#     python lyrics_gen.py --numlines=<number-of-lines-to-generate>
# Notes:
#     As we use TSP-based rhyme selection (=> brute force),
#     the maximum number of lines is limited.
#     See rd_join.py for details.

import random
import sys
from RNN import sample as rnn_sample
from rap_word2vec import RapWord2Vec

num_lines = None
for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    if arg.startswith('--numlines='):
        num_lines = int(arg[len('--numlines='):])
if num_lines is None:
    raise RuntimeError('Supply the number of lines to generate on the command line')

rw2v = RapWord2Vec()
sampler = rnn_sample.Sampler()

# removes type suffix concatenated by text processor
# Ex> '찬란하다/Verb' --> '찬란하다'
def remove_word_type_suffix(word):
    word = str(word)
    if '/' in word:
        return word.rsplit('/', 1)[0]
    return word
print('asd')
lines = []
for _ in range(num_lines):
    a, b = rw2v.generate_words(' ', ' ')
    a = remove_word_type_suffix(a)
    b = remove_word_type_suffix(b)
    sampler.set_prime_text(a)
    a_len = random.randrange(5, 8)
    s = sampler.sample(a_len)
    print(s)
    line = s + ' ' + b
    sampler.set_prime_text(line)
    b_len = len(line) + random.randrange(5, 8)
    line = sampler.sample(b_len)
    line = line.replace('\n', ' ').replace('  ', ' ').strip()
    lines.append([a, b, line])

for line in lines:
    print(line)
