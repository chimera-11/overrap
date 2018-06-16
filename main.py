import hangul
import strutils
from rap_word2vec_180514 import RapWord2Vec180514
from linegen import LineGen
from rnn_lyrics_gen_180514_constraint import RNNLyricsGen180514Constraint
from rd_eval import RhymeDensityEval

N = 4
C = 20
T = 4
w2v = RapWord2Vec180514()
lg = LineGen()
r = RhymeDensityEval()
#fixer = RNNLyricsGen180514Constraint('crawl_dance_180514')
fixer = RNNLyricsGen180514Constraint('..\\crawl_dance')

compatible_classes = {
    '아': ['아', '와'],
    '야': ['야'],
    '어': ['어', '워'],
    '여': ['여', '어'],
    '오': ['오'],
    '요': ['요'],
    '우': ['우'],
    '유': ['유'],
    '으': ['으'],
    '이': ['이', '위', '의'],
    '애': ['애', '에', '왜', '외', '얘'],
    '에': ['에', '애', '왜', '웨', '외', '예'],
    '왜': ['왜', '애', '웨', '외'],
    '웨': ['웨', '왜', '에', '외'],
    '외': ['외', '웨', '왜', '에'],
    '의': ['의', '이', '위'],
    '위': ['위', '이', '의'],
    '얘': ['얘', '예'],
    '예': ['예', '얘'],
    '와': ['와', '아'],
    '워': ['워', '어']
}

def locate_vset(vindex):
    for k, v in compatible_classes.items():
        if hangul.get_vowel_index(k) == vindex:
            return v
    return None # shouldn't happen

# Fixes target string to have the same
# ending rhyme with template, using
# the ending vowel of template
def fix_line_ending(template, target):
    vindices = None # vowel index
    for c in reversed(template):
        if hangul.is_hangul_char(c):
            vindex = hangul.get_vowel_index(c)
            vset = locate_vset(vindex)
            vindices = [hangul.phoneme_to_index(
                hangul.joongseongs[hangul.get_vowel_index(x)]
                ) for x in vset]
            break
    if vindices == None:
        return target # we can't change
    target_fixed_str = ''
    target_prob = 0
    def try_update(target):
        nonlocal target_fixed_str
        nonlocal target_prob
        for vindex in vindices:
            #for last_char in [' ', '\n']:
            for last_char in ['\n']:
                for cst_len in [4, 5, 6, 7]:
                    char_constraint = [-1] * cst_len
                    char_constraint[-3] = vindex
                    char_constraint[-1] = hangul.phoneme_to_index(last_char)
                    fixed_str, prob = fixer.run(target, char_constraint, pruning_prob=target_prob)
                    if prob > target_prob:
                        target_fixed_str, target_prob = fixed_str, prob
    #try_update(target)
    #try_update(lg.run(target, 1))
    try_update(target[:-1])
    try_update(target[:-2])
    return strutils.normalize(target_fixed_str)

def lines2str(lines):
    result = ''
    for line in lines:
        result += line + '\n'
    return result

lines = []
lines.append(lg.generate('\n', 14)[1:])
for i in range(N - 1):
    prev_line = lines[-1]
    prev_lines = lines2str(lines)
    pre_candidates = lg.generate_multi(prev_lines, 11, C)
    candidates = []
    for cand in pre_candidates:
        cand = cand[len(prev_lines):]
        if len(cand) >= 14:
            pass
        score = r.eval_between(prev_line, cand)
        candidates.append((cand, score))
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    print(candidates)
    next = ['', -1]
    for j in range(min(T, len(candidates))):
        cand = candidates[i][0]
        cand = fix_line_ending(lines2str(lines), cand)
        score = r.eval_between_line_endings(prev_line, cand)
        if score > next[1]:
            next = [cand, score]
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
