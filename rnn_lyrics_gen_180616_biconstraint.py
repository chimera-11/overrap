# ---------------------------------------------
#   rnn_lyrics_gen_180616_biconstraint.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module generates lyrics based on 
#     trained RNN model, taking into account the string
#     in the leading and trailing position
# Usage:
#     python rnn_lyrics_gen_180616_biconstraint.py <model-path> <leading-phase> <trailing-phase> <char#-to-generate>
# Notes:
#     The suffix '180616' indicates the major revision date.
#     The model should match that of rnn_lyrics_train_180616.py.
#     Otherwise errors will occur during model import.
#     The character constraint should be a list of integers [-1..69]
#     each specifying which pivots a character there.
#     Here, -1 means a position do not have any constraints.
#     As the algorithm runs brute force (beam search) using
#     the softmax probabilities, it is recommended to keep the
#     length of the character constraint below 5.
# Warning:
#     Command-line specification of character constraint is
#     yet to be implemented! (If you wish to test, please
#     refer to the code at the bottom of this file)

import tensorflow as tf
import sys
import hangul
import hangul_comp
import hangul_decomp
import numpy as np
import mathutils
import os
from wordset import Wordset


class RNNLyricsGen180616Biconstraint:
    def __init__(self, model_path):
        self.model_path = model_path
        wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']
        self.wordset = Wordset(wordset)
    def run(self, leading, trailing, num_chars, vindices=None):
        results = self.run_multi(leading, trailing, num_chars, 2, vindices)
        probs = np.array([x[1] for x in results])
        probs = probs / np.sum(probs)
        idx = np.random.choice(len(probs), p=probs)
        return results[idx]
    # vindices: allowed vowel index for last character
    def run_multi(self, leading, trailing, num_chars, gen_count, vindices=None):
        with tf.Graph().as_default():       # use local graph, prevent parameter duplicate issue
            model_path = self.model_path
            wordset = self.wordset

            n_inputs = len(wordset)     # number of features (= wordset size)
            n_steps = 15                # length of input sequence
            n_neurons = 256             # learning capacity of the network (pretty much arbitrary)
            n_layers = 3                # number of layers
            n_outputs = len(wordset)    # number of output classes (= wordset size)

            X = tf.placeholder(tf.float32, [1, n_steps, n_inputs])

            cells = []
            for i in range(n_layers):
                cell_name = 'cell%d' % i
                cell = tf.contrib.rnn.GRUCell(num_units=n_neurons, name=cell_name)
                cells.append(cell)
            cell = tf.contrib.rnn.MultiRNNCell(cells)
            seq_length = tf.placeholder(tf.int32, [None])
            # outputs = [batch_size, max_time, cell.output_size]
            init_states = cell.zero_state(1, tf.float32)
            outputs, states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32,
                sequence_length=seq_length, initial_state=init_states)

            logits = tf.contrib.layers.fully_connected(outputs, n_outputs, activation_fn=None)
            #xentropy = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)

            init = tf.global_variables_initializer()

            leading_str_decomp = hangul_decomp.process_data(leading)
            seq_len_default = n_steps

            self.best_seqs = [('가사 생성 실패', -1)]

            config = tf.ConfigProto(
                    device_count = {'GPU': 0} # don't use GPU for generation
                )
            with tf.Session(config=config) as sess:
                init.run()
                saver = tf.train.Saver()
                checkpoint_file = os.path.join(model_path, "checkpoint-180616")
                saver_file = os.path.join(model_path, "model-180616.ckpt")
                if not os.path.isfile(checkpoint_file):
                    raise EnvironmentError("Couldn't fild the trained data file 'model-180616.ckpt' in the target directory")
                saver.restore(sess, saver_file)
                def predict_phoneme(decomposed_seq, prev_state):
                    input_str = decomposed_seq[-seq_len_default:]
                    X_run, seq_len_run = wordset.bake_up_run(input_str, seq_len_default)
                    X_run = np.reshape(X_run, (-1, n_steps, n_inputs))
                    c, new_state = sess.run([logits, states],
                        feed_dict={X: X_run, seq_length: [seq_len_run], init_states: prev_state})
                    c = c[0][seq_len_run-1]
                    c = mathutils.softmax(c)
                    return c, new_state
                def calc_prob(prev_state, primer, trailer):
                    primer = hangul_decomp.process_data(primer)
                    trailer = hangul_decomp.process_data(trailer)
                    states = prev_state
                    prob = 1.0
                    for c in list(trailer):
                        probs, states = predict_phoneme(primer, states)
                        cindex = hangul.phoneme_to_index(c)
                        prob *= probs[cindex]
                        primer += c
                    return prob
                def calc_candidates(prev_state, primer, depth=-1, dfs_char_depth=-1):
                    decomposed_seq = hangul_decomp.process_data(primer)
                    # returns a list of (char, prob, state) tuple
                    result = []
                    # 1. hangul
                    window = [(0, len(hangul.choseongs)),
                        (len(hangul.choseongs), len(hangul.choseongs) + len(hangul.joongseongs)),
                        (len(hangul.choseongs) + len(hangul.joongseongs), len(hangul.choseongs) + len(hangul.joongseongs) + len(hangul.jongseongs))]
                    def char_dfs(inner_state, decomposed_seq, char_depth, prob, dfs_char_depth):
                        if char_depth == 3:
                            c = hangul_comp.process_data(decomposed_seq[-3:])
                            result.append((c, pow(prob, 1/3), inner_state))
                            return
                        probs, state = predict_phoneme(decomposed_seq, inner_state)
                        if dfs_char_depth == num_chars - 1 and char_depth == 1 and vindices is not None:
                            probs_old = probs
                            probs = []
                            for cidx in vindices:
                                probs.append((cidx, probs_old[cidx]))
                        else:
                            probs = list(enumerate(probs))[window[char_depth][0]:window[char_depth][1]]
                        probs = sorted(probs, key=lambda x: x[1], reverse=True)
                        for j in range(min(3, len(probs))):
                            cidx, cprob = probs[j]
                            c = hangul.default_wordset[cidx]
                            char_dfs(state, decomposed_seq + c, char_depth + 1, prob * cprob, dfs_char_depth)
                    char_dfs(prev_state, decomposed_seq, 0, 1.0, dfs_char_depth)
                    # 2. space and newline
                    # note that 1) we don't allow them to appear in a row
                    #    and 2) we don't allow the last character to be space or newline
                    if depth < num_chars - 1 and (primer[-1] != ' ' and primer[-1] != '\n'):
                        probs, state = predict_phoneme(decomposed_seq, prev_state)
                        idx = wordset.char_to_index(' ')
                        result.append((' ', probs[idx], state))
                        idx = wordset.char_to_index('\n')
                        result.append(('\n', probs[idx], state))
                    result = sorted(result, key=lambda x: x[1], reverse=True)
                    end = 2
                    if depth <= 2:
                        end = 3
                    result = result[0:end]
                    #print(result[0][0]+result[1][0]+result[2][0])
                    return result
                def dfs(depth, char_depth, cur_str, prob, prev_state):
                    if prob < self.best_seqs[-1][1]:
                        return # early pruning
                    if char_depth >= num_chars:
                        prob *= calc_prob(prev_state, cur_str, trailing)
                        # try update 
                        if prob > self.best_seqs[-1][1]:
                            self.best_seqs.append((cur_str, prob))
                            self.best_seqs = sorted(self.best_seqs, key=lambda x:x[1], reverse=True)
                            if len(self.best_seqs) > gen_count:
                                self.best_seqs = self.best_seqs[0:gen_count]
                            pass
                        return
                    # beam search (branching factor = 3)
                    next_candidates = calc_candidates(prev_state, cur_str, depth, char_depth)
                    for (c, p, next_state) in next_candidates:
                        char_depth_new = char_depth if c in [' ', '\n'] else char_depth + 1
                        dfs(depth, char_depth_new, cur_str + c, prob * p, next_state)
                dfs(0, 0, leading_str_decomp, 1, sess.run(cell.zero_state(1, tf.float32)))
                if __name__ == '__main__':
                    if self.best_seqs[0][1] == -1:
                        self.best_seqs = ['Failed to generate', 0]
                    else:
                        print(self.best_seqs[0][1])
                for i in range(len(self.best_seqs)):
                    (return_str, prob) = self.best_seqs[i]
                    self.best_seqs[i] = (hangul_comp.process_data(return_str), prob)
        return self.best_seqs

if __name__  == '__main__':
    model_path = sys.argv[1]
    leading = sys.argv[2]
    trailing = sys.argv[3]
    num_chars = int(sys.argv[4])
    rnn = RNNLyricsGen180616Biconstraint(model_path)
    obj = rnn.run_multi(leading, trailing, num_chars, 4)
    print(obj)
    (output_str, avg_prob) = obj[0]
    print(list(output_str))
    output_str = output_str.replace('\n', ' ').replace('  ', ' ')
    print(output_str)
    print(avg_prob)