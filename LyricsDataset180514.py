# '_' prefix indicates that the function is intended to be only used within this file

import numpy as np
import os
import random
import hangul_decomp

def _read_file_decompose_hangul(path):
    with open(path, 'r', encoding='utf8') as myfile:
        data = myfile.read()
    return hangul_decomp.process_data(data)

class LyricsDataset180514:
    def __init__(self, path, wordset, seq_len_default, seq_len_min):
        self.path = path
        self.wordset = wordset
        self.seq_len_default = seq_len_default
        self.seq_len_min = seq_len_min
        self.reset()
    def reset(self):
        self.counter = -1
        self.file_list = []
        for _, _, files in os.walk(self.path):  
            for filename in files:
                if filename.endswith('.txt'):
                    self.file_list.append(filename) # only use text files (not .ckpt files)
        random.shuffle(self.file_list)
        self.next_file_to_fetch = 0
        self._fetch_next_file()
    def next_batch(self, batch_size):
        X = np.zeros((batch_size, self.seq_len_default, len(self.wordset)))
        Y = np.zeros((batch_size, self.seq_len_default, len(self.wordset)))
        SeqLen = np.zeros(batch_size)
        for i in range(batch_size):
            x, y, seq_len = self.next_training_example()
            X[i,:,:] = x
            Y[i,:,:] = y
            SeqLen[i] = seq_len
        return X, Y, SeqLen
    def next_training_example(self):
        successful = False
        while not successful:
            successful, data = self.try_extract_next()
            if successful:
                return data
            self._fetch_next_file()
    def try_extract_next(self):
        while self.file_content_pos < self.file_content_len:
            window_len_max = min(self.file_content_pos, self.seq_len_default)
            pos = self.file_content_pos
            for window_len in range(window_len_max, self.seq_len_min-1, -1):
                if self._is_in_wordset(self.file_content[pos-window_len:pos+1]):
                    self.file_content_pos += 1
                    return True, self._bake_up_train(window_len, pos)
            self.file_content_pos += 1
        return False, None
    def _fetch_next_file(self):
        prev_cwd = os.getcwd()
        os.chdir(self.path)
        filename = self.file_list[self.next_file_to_fetch]
        if self.next_file_to_fetch is 0:
            self.counter += 1
        self.next_file_to_fetch = (self.next_file_to_fetch + 1) % len(self.file_list)
        self.file_content = _read_file_decompose_hangul(filename)
        self.file_content_pos = self.seq_len_min
        self.file_content_len = len(self.file_content)
        os.chdir(prev_cwd)
        return
    def _is_in_wordset(self, test_str):
        for c in list(test_str):
            if not c in self.wordset:
                return False
        return True
    def _bake_up_train(self, window_len, pos):
        x = np.zeros((self.seq_len_default, len(self.wordset)))
        y = np.zeros((self.seq_len_default, len(self.wordset)))
        for i in range(window_len):
            x[i,:] = self._one_hot(self.file_content[pos-window_len+i])
            y[i,:] = self._one_hot(self.file_content[pos-window_len+i+1])
        seq_len = window_len
        return x, y, seq_len
    def _one_hot(self, c):
        x = np.zeros(len(self.wordset))
        x[self._char_to_index(c)] = 1
        return x
    def _char_to_index(self, c):
        return self.wordset.index(c)