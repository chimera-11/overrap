import hangul
import strutils
from rap_word2vec_180514 import RapWord2Vec180514
from linegen import LineGen
from rnn_lyrics_gen_180514_constraint import RNNLyricsGen180514Constraint
from rnn_lyrics_gen_180514_biconstraint import RNNLyricsGen180514Biconstraint
from rnn_lyrics_gen_180616_biconstraint import RNNLyricsGen180616Biconstraint
from rd_eval import RhymeDensityEval

C = 20
T = 4
w2v = RapWord2Vec180514()
lg = LineGen()
r = RhymeDensityEval()
fixer = RNNLyricsGen180514Constraint('crawl_dance_180514')
#gap_filler = RNNLyricsGen180514Biconstraint('crawl_dance_180514')
gap_filler = RNNLyricsGen180616Biconstraint('..\\crawl_dance_180606')

compatible_classes = {
    '아': ['아', '와'],
    '야': ['야', '아'],
    '어': ['어', '워'],
    '여': ['여', '어'],
    '오': ['오'],
    '요': ['요'],
    '우': ['우'],
    '유': ['유'],
    '으': ['으', '이'],
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

def get_vindices(template):
    vindices = None # vowel index
    for c in reversed(template):
        if hangul.is_hangul_char(c):
            vindex = hangul.get_vowel_index(c)
            vset = locate_vset(vindex)
            vindices = [hangul.phoneme_to_index(
                hangul.joongseongs[hangul.get_vowel_index(x)]
                ) for x in vset]
            break
    return vindices

# Fixes target string to have the same
# ending rhyme with template, using
# the ending vowel of template
def fix_line_ending(template, target):
    vindices = get_vindices(template)
    if vindices == None:
        return target # we can't change
    target_fixed_str = ''
    target_prob = 0
    def try_update(target):
        nonlocal target_fixed_str
        nonlocal target_prob
        for vindex in vindices:
            print(hangul.default_wordset[vindex])
            #for last_char in [' ', '\n']:
            for last_char in ['\n']:
                for cst_len in [4, 5, 6]:
                    char_constraint = [-1] * cst_len
                    char_constraint[-3] = vindex
                    char_constraint[-1] = hangul.phoneme_to_index(last_char)
                    fixed_str, prob = fixer.run(target, char_constraint, pruning_prob=target_prob)
                    if prob > target_prob:
                        target_fixed_str, target_prob = fixed_str, prob
    try_update(target[:-1])
    try_update(target[:-2])
    return strutils.normalize(target_fixed_str), target_prob

def lines2str(lines):
    result = ''
    for line in lines:
        result += line + '\n'
    return result

w1, w2 = w2v.sample_pair()
w3 = w2v.sample_pair(w2)[1]
print('w1=%s, w2=%s, w3=%s' % (w1, w2, w3))
#w1 = w1[0:3]
#w2 = w2[0:3]
#w3 = w3[0:3]

start_words = [w1, w2, '', w3, '']
#start_words = [w1, w2, '']
lines = []
prev_concat = ''
L = len(start_words) - 1

for i in range(L):
    start_word = start_words[i]
    trailer = start_words[i + 1]
    if len(trailer) > 0:
        def gen_with_biconstraint():
            print('Sandwich modulation in progress...')
            primer = prev_concat + start_word
            count = 10 - len(start_word)
            line = start_word + lg.generate(primer, count, include_primer=False)
            line = line[:len(start_word) + count]
            vindices = get_vindices(lines[i - 1]) if i > 0 else None
            line = gap_filler.run(primer + line, '\n' + trailer, 4, vindices=vindices)[0]
            line = line[len(primer):]
            line = strutils.normalize(line)
            print('Sandwich modulation done')
            return line
        if i == 0:
            line = gen_with_biconstraint()
            lines.append(line)
            prev_concat += line + '\n'
            print(line)
        else:
            cands = []
            for _ in range(4):
                line = gen_with_biconstraint()
                score = r.eval_between(lines[i - 1], line)
                cands.append((line, score))
            cands = sorted(cands, key=lambda x: x[1], reverse=True)
            print(cands)
            line = cands[0][0]
            #line, _ = fix_line_ending(lines[i - 1], line)
            lines.append(line)
            prev_concat += line + '\n'
            print(line)
    else:
        count = 14 - len(start_word)
        pre_candidates = lg.generate_multi(prev_concat + start_word, count, C)
        candidates = []
        for cand in pre_candidates:
            cand = cand[len(prev_concat):]
            cand = strutils.normalize(cand)
            if len(cand) >= 15:
                pass
            score = r.eval_between(prev_concat, cand)
            candidates.append((cand, score))
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        print(candidates)
        next = ['', -1]
        for j in range(min(T, len(candidates))):
            cand = candidates[i][0]
            cand, score = fix_line_ending(prev_concat, cand)
            if score > next[1]:
                next = [cand, score]
        line = next[0]
        lines.append(line)
        prev_concat += line + '\n'
print(prev_concat)
'''
line1 = lg.generate(w1, 5)
line1 = gap_filler.run(line1, ' ' + w2, 4)[0]
line1 = strutils.normalize(line1)
print(line1)
line2 = gap_filler.run(line1 + ' ' + w2, '', 3)[0]
line2 = line2[len(line1) + 1:]
line2 = lg.generate(line1 + ' ' + line2, 7)
line2 = line2[len(line1) + 1:]
print(line2)
line2 = fix_line_ending(line1, line2)
print(line1)
print(line2)
line3 = gap_filler.run(line1 + ' ' + line2, '\n' + w3, 5)[0]
line3 = line2[len(line1) + 1:]
line3 = strutils.normalize(line2)
print(line2)
line3 = lg.generate(line1 + ' ' + line2 + '\n', 12, include_primer=False)
print(line3)
line3 = fix_line_ending(line2, line3)
print(line1)
print(line2)
print(line3)
#line4 = lg.generate(line1 + ' ' + line2 + '\n' + line3 + '\n' + w3)
'''



'''
lines.append(lg.generate(' ', 14)[1:])
for i in range(N - 1):
    prev_line = lines[-1]
    prev_lines = lines2str(lines)
    gap_filler.generate_multi()
    pre_candidates = lg.generate_multi(prev_lines, 11, C)
    candidates = []
    for cand in pre_candidates:
        cand = cand[len(prev_lines):]
        if len(cand) >= 13:
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
