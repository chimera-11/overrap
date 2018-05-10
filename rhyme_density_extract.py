
# 1. generate training example
# 2. 

import hangul
import input_timer
import os
import sys
import numpy as np

# usage: python rhyme_density_extract.py <rhyme text-containing folder path>

#data_src_path = 'crawl_hiphop'
#data_src_path = sys.argv[1]
#data_src_path = '..\\op'
data_src_path = '..\\tmp'
verbose = False

class RhymeDensityModule:
    def __init__(self):
        self._unrelate_table = self.create_empty_matrix()
        self._nonegate_table = self.create_empty_matrix()
        self._unrelate_append('아유')
        self._unrelate_append('야우')
        self._unrelate_append('야우')
        self._nonegate_append('애에')
        self._nonegate_append('애웨')
        self._nonegate_append('애웨')
        self._nonegate_append('애예')
        self._nonegate_append('에예')
        self._nonegate_append('애예')
        self._nonegate_append('위이')
        self._nonegate_append('외이')
        self._nonegate_append('와아')
        self._nonegate_append('워어')
        self._nonegate_append('의이')
        self._nonegate_append('의으')
        self._nonegate_append('우유')
        self._nonegate_append('으우')
    def _unrelate_append(self, vowel_str):
        v1 = hangul.get_vowel_index(vowel_str[0])
        v2 = hangul.get_vowel_index(vowel_str[1])
        self._unrelate_table[v1][v2] = 1
        self._unrelate_table[v2][v1] = 1
    def _nonegate_append(self, vowel_str):
        v1 = hangul.get_vowel_index(vowel_str[0])
        v2 = hangul.get_vowel_index(vowel_str[1])
        self._nonegate_table[v1][v2] = 1
        self._nonegate_table[v2][v1] = 1
    def create_empty_matrix(self):
        num_vowels = hangul.num_vowels()
        table = []
        for _ in range(0, num_vowels):
            table.append([0] * num_vowels)
        return table
    def init_default_parameters(self):
        self._table = self.create_empty_matrix()
        for i in range(0, hangul.num_vowels()):
            self._table[i][i] = 1
        self._threshold = 0
    def init_rhyme_storage(self):
        self._table_new = self.create_empty_matrix()
        self._table_vowel_cnt = [0] * hangul.num_vowels()
        self._rhyme_cnt = 0
        self._train_examples = []
        self._train_numtrue = 0
    def update_parameters(self, learning_rate=0.5, decay_rate=0.0):
        num_vowels = hangul.num_vowels()
        vowel_cnt = sum(self._table_vowel_cnt)
        for i in range(0, num_vowels):
            for j in range(0, num_vowels):
                prob_rhyme = self._table_new[i][j] / self._rhyme_cnt
                prob_nonrhyme = (self._table_vowel_cnt[i] / vowel_cnt) * (self._table_vowel_cnt[j] / vowel_cnt)
                if self._table_new[i][j] > 0 and self._table_vowel_cnt[i] > 0 and self._table_vowel_cnt[j] > 0:
                    new_val = np.log(prob_rhyme / prob_nonrhyme) # log-odds
                    self._table[i][j] += (new_val - self._table[i][j]) * learning_rate
        #if self._rhyme_cnt > 0 or self._nonrhyme_cnt > 0:
        #   self._threshold = self._threshold +
        #   (self._threshold - ((self._rhyme_cnt) / (self._rhyme_cnt + self._nonrhyme_cnt))) * learning_rate
        # update threshold
        self.update_threshold()
        # prepare for next step
        self.init_rhyme_storage()
    def update_threshold(self):
        train_sorted = sorted(self._train_examples, key=lambda x: x[0], reverse=True)
        tp_count = 0
        p_count = 0
        max_F1_thr = 0
        max_F1 = 0
        for score, is_rhyme in train_sorted: # include examples with (rhyme_score) >= score
            if is_rhyme:
                tp_count += 1
            p_count += 1
            precision = tp_count / p_count
            recall = tp_count / self._train_numtrue
            F1_score = 2 * precision * recall / (precision + recall)
            if F1_score > max_F1:
                max_F1 = F1_score
                max_F1_thr = score
        self._threshold = max_F1_thr
    def vowel_similarity(self, vowel1, vowel2):
        #if self._unrelate_table[vowel1][vowel2] == 1:
        #    return -10
        return self._table[vowel1][vowel2]
    def score_rhyme(self, vowels1, vowels2):
        if len(vowels1) != len(vowels2):
            raise RuntimeError('You must supply vowel phrases of equal length')
        vlen = len(vowels1)
        similarity_score = 0
        for i in range(0, vlen):
            v1 = vowels1[i]
            v2 = vowels2[i]
            similarity_score += self.vowel_similarity(v1, v2)
        return similarity_score
    def add_match(self, phrase1, phrase2):
        if len(phrase1) != len(phrase2):
            raise RuntimeError('You must supply phrases of equal length')
        f1, vowels1 = hangul.convert_to_vowel_indices(phrase1)
        f2, vowels2 = hangul.convert_to_vowel_indices(phrase2)
        if f1 and f2:
            score = self.score_rhyme(vowels1, vowels2)
            is_rhyme = score >= self._threshold
            self._train_examples.append([score, is_rhyme])
            if is_rhyme:
                self._train_numtrue += 1
                if verbose:
                    print('%s + %s' % (phrase1, phrase2))
                for i in range(0, len(phrase1)):
                    v1 = vowels1[i]
                    v2 = vowels2[i]
                    #if not is_rhyme and self._nonegate_table[v1][v2] == 1:
                    #    continue
                    self._table_new[v1][v2] += 1
                    if v1 != v2:
                        self._table_new[v2][v1] += 1
                    self._rhyme_cnt += 1
            for v in vowels1:
                self._table_vowel_cnt[v] += 1
            for v in vowels2:
                self._table_vowel_cnt[v] += 1
    def add_matches_within(self, input_string):
        # length 2, 3, 4
        input_string = input_string.replace(' ', '').replace('\r','').replace('\n','')
        input_len = len(input_string)
        for L in [2,3,4]:
            for i in range(0, input_len - L + 1):
                for j in range(i + L, input_len - L + 1):
                    self.add_match(input_string[i:i+L], input_string[j:j+L])

r = RhymeDensityModule()
r.init_default_parameters()
r.init_rhyme_storage()

file_list = []
for _, _, files in os.walk(data_src_path):
    for filename in files:
            if filename.endswith('.txt'):
                file_list.append(filename)


prev_cwd = os.getcwd()
os.chdir(data_src_path)
while True:
    i = 1
    for filename in file_list:
        with open(filename, 'r', encoding='utf8') as lyrics_file:
            lines = lyrics_file.readlines()
        for line in lines:
            r.add_matches_within(line)
        #for j in range(0, len(lines)-1):
        #   r.add_matches_within(lines[j] + lines[j+1])
        if i % 100 == 0 or i == len(file_list):
            print("%dth file processed" % i)
            i = i + 1
        else:
            i = i + 1
            continue
        try:
            c = input_timer.input("press any key to pause", 0.5)
        except TimeoutError:
            continue
        reenter = True
        while reenter:
            c = input_timer.input("press 't' to test; any other key to go forward", 1000000)
            if c == 't':
                while True:
                    word1, word2 = input('').split()
                    f1, vowels1 = hangul.convert_to_vowel_indices(word1)
                    f2, vowels2 = hangul.convert_to_vowel_indices(word2)
                    if not f1 or not f2:
                        continue
                    val = r.score_rhyme(vowels1, vowels2)
                    print('%f' % val)
                    break
            elif c == 'p':
                print(r._table)
                print('Current threshold value: %f' % r._threshold)
            elif c == 'v-on':
                verbose = True
            elif c == 'v-off':
                verbose = False
            else:
                reenter = False
    r.update_parameters()
os.chdir(prev_cwd)

print(r._table)
