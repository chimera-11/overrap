import hangul
import strutils
from rap_word2vec_180514 import RapWord2Vec180514
from linegen import LineGen
from rnn_lyrics_gen_180514_constraint import RNNLyricsGen180514Constraint
from rd_eval import RhymeDensityEval

N = 4
T = 5
w2v = RapWord2Vec180514()
lg = LineGen()
r = RhymeDensityEval()
fixer = RNNLyricsGen180514Constraint('crawl_dance_180514')

# Fixes target string to have the same
# ending rhyme with template, using
# the ending vowel of template
def fix_line_ending(template, target):
    vindex = -1 # vowel index
    for c in reversed(template):
        if hangul.is_hangul_char(c):
            vindex = hangul.get_vowel_index(c)
            vindex = hangul.phoneme_to_index(hangul.joongseongs[vindex])
            break
    if vindex == -1:
        return target # we can't change
    target_fixed_str = ''
    target_prob = 0
    def try_update(target):
        nonlocal target_fixed_str
        nonlocal target_prob
        for cst_len in [6, 7, 8]:
            char_constraint = [-1] * cst_len
            char_constraint[-3] = vindex
            char_constraint[-1] = hangul.phoneme_to_index(' ')
            fixed_str, prob = fixer.run(target, char_constraint, pruning_prob=target_prob)
            if prob > target_prob:
                target_fixed_str, target_prob = fixed_str, prob
    try_update(target)
    try_update(target[:-1])
    return strutils.normalize(target_fixed_str)

lines = []
lines.append(lg.generate(' ', 12)[1:])
for i in range(N - 1):
    next = ['', -1]
    prev_line = lines[-1]
    for j in range(T):
        next_cand = lg.generate(prev_line + '\n', 12)
        next_cand = next_cand[len(prev_line):]
        next_cand = fix_line_ending(prev_line, next_cand)
        score = r.eval_between_line_endings(prev_line, next_cand)
        if score > next[1]:
            next = [next_cand, score]
    lines.append(next[0])
for line in lines:
    print(line)
'''
seq = [0]

for i in range(9):
    last_idx = seq[-1]
    next_cand = [0, -1]
    for j in range(N):
        if j in seq:
            continue
        score = r.eval_between_line_endings(lines[last_idx], lines[j])
        if score > next_cand[1]:
            next_cand = [j, score]
    seq.append(next_cand[0])
for i in seq:
    print(lines[i])
'''
