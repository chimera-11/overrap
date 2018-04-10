import numpy as np
import hangul

class Wordset:
    def __init__(self, wordset):
        self.wordset = wordset
    def __len__(self):
        return len(self.wordset)
    def is_in_wordset(self, test_str):
        for c in list(test_str):
            if not c in self.wordset:
                return False
        return True
    def bake_up_train(self, src_str, dst_chr, seq_len_default):
        x, seq_len = self.bake_up_run(src_str, seq_len_default)
        y = self.one_hot(dst_chr)
        return x, y, seq_len
    def bake_up_run(self, src_str, seq_len_default):
        seq_len = len(src_str)
        x = np.zeros((seq_len_default, len(self.wordset)))
        for i in range(seq_len):
            x[i,:] = self.one_hot(src_str[i])
        return x, seq_len
    def one_hot(self, c):
        x = np.zeros(len(self.wordset))
        x[self.char_to_index(c)] = 1
        return x
    def sample_context_aware(self, weights, option=None):
        if option is "choseong":
            return self.sample_from_subset(weights, hangul.joongseongs)
        elif option is "joongseong":
            return self.sample_from_subset(weights, hangul.jongseongs)
        elif option is "jongseong" or option is "not_hangul":
            return self.sample_from_subset(weights, \
                [c for c in self.wordset if c not in hangul.joongseongs and c not in hangul.jongseongs])
        elif option is None:
            return self.sample_from(weights)
        else:
            raise ValueError("option is invalid: supplied value is " + str(option))
    def sample_from_subset(self, weights, subset):
        one_hot = np.zeros(len(self.wordset))
        for i in range(len(self.wordset)):
            if self.wordset[i] in subset:
                one_hot[i] = 1
        new_weights = weights * one_hot
        new_weights /= np.sum(new_weights)
        return self.sample_from(new_weights)
    def sample_from(self, weights):
        #return self.wordset[np.argmax(weights)]
        return np.random.choice(self.wordset, p=weights)
    def char_to_index(self, c):
        return self.wordset.index(c)