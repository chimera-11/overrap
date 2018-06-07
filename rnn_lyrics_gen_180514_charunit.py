# ---------------------------------------------
#   rnn_lyrics_gen_180514_charunit.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module generates lyrics based on 
#     trained RNN model.
#     The difference from vanilla generator is that
#     this module performs sampling on character level,
#     not on phoneme level.
# Usage:
#     python rnn_lyrics_gen_180514_charunit.py <model-path> <priming-phrase> <#-of-char-to-append>
# Notes:
#     The suffix '180514' indicates the major revision date.
#     The model should match that of rnn_lyrics_train_180514.py.
#     Otherwise errors will occur during model import.

import tensorflow as tf
import sys
import hangul
import hangul_comp
import hangul_decomp
import numpy as np
import mathutils
import os
from wordset import Wordset


class RNNLyricsGen180514:
    def __init__(self, model_path):
        self.model_path = model_path
    def run(self, start_str, append_count):
        return self.run_multi(start_str, append_count, 1)[0]
    def run_multi(self, start_str, append_count, generate_count):
        with tf.Graph().as_default():       # use local graph, prevent parameter duplicate issue
            model_path = self.model_path

            wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']
            wordset = Wordset(wordset)

            n_inputs = len(wordset)     # number of features (= wordset size)
            n_steps = 30                # length of input sequence
            n_neurons = 512             # learning capacity of the network (pretty much arbitrary)
            n_layers = 4                # number of layers
            n_outputs = len(wordset)    # number of output classes (= wordset size)

            X = tf.placeholder(tf.float32, [1, n_steps, n_inputs])

            cells = []
            for i in range(n_layers):
                cell_name = 'cell%d' % i
                cell = tf.contrib.rnn.BasicLSTMCell(num_units=n_neurons, name=cell_name)
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

            output_count_target = len(start_str) + append_count
            seq_len_default = 30

            config = tf.ConfigProto(
                    device_count = {'GPU': 0} # don't use GPU for generation
                )
            results = []
            with tf.Session(config=config) as sess:
                init.run()
                saver = tf.train.Saver()
                checkpoint_file = os.path.join(model_path, "checkpoint")
                saver_file = os.path.join(model_path, "model-180514.ckpt")
                if not os.path.isfile(checkpoint_file):
                    raise EnvironmentError("Couldn't fild the trained data file 'model-180514.ckpt' in the target directory")
                saver.restore(sess, saver_file)
                for lstmcell in cells:
                    lstmcell.zero_state(1, tf.float32)
                for _ in range(generate_count):
                    output_str = start_str
                    return_str = ''
                    '''
                    for i in range(len(output_str)):
                        input_str = output_str[0:i]
                        if len(input_str) < 5:
                            continue
                        if len(input_str) > seq_len_default:
                            input_str = input_str[-seq_len_default:]
                        X_run, seq_len_run = wordset.bake_up_run(input_str, seq_len_default)
                        X_run = np.reshape(X_run, (-1, n_steps, n_inputs))
                        c, _ = sess.run([logits, states], feed_dict={X: X_run, seq_length: [seq_len_run]})
                    '''
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
                    def calc_candidates(prev_state, primer):
                        decomposed_seq = hangul_decomp.process_data(primer)
                        # returns a list of (char, prob, state) tuple
                        result = []
                        # 1. hangul
                        window = [(0, len(hangul.choseongs)),
                            (len(hangul.choseongs), len(hangul.choseongs) + len(hangul.joongseongs)),
                            (len(hangul.choseongs) + len(hangul.joongseongs), len(hangul.choseongs) + len(hangul.joongseongs) + len(hangul.jongseongs))]
                        def char_dfs(inner_state, decomposed_seq, depth, prob):
                            if depth == 3:
                                c = hangul_comp.process_data(decomposed_seq[-3:])
                                result.append((c, pow(prob, 1/3), inner_state))
                                return
                            probs, state = predict_phoneme(decomposed_seq, inner_state)
                            probs = list(enumerate(probs))[window[depth][0]:window[depth][1]]
                            probs = sorted(probs, key=lambda x: x[1], reverse=True)
                            for j in range(3):
                                cidx, cprob = probs[j]
                                c = hangul.default_wordset[cidx]
                                char_dfs(state, decomposed_seq + c, depth + 1, prob * cprob)
                        char_dfs(prev_state, decomposed_seq, 0, 1.0)
                        # 2. space and newline
                        # note that we don't allow them to appear in a row
                        probs, state = predict_phoneme(decomposed_seq, prev_state)
                        if primer[-1] != ' ' and primer[-1] != '\n':
                            idx = wordset.char_to_index(' ')
                            result.append((' ', probs[idx], state))
                            idx = wordset.char_to_index('\n')
                            result.append(('\n', probs[idx], state))
                        result = sorted(result, key=lambda x: x[1], reverse=True)
                        result = result[0:7]
                        return result
                    state = sess.run(cell.zero_state(1, tf.float32))
                    while len(output_str) < output_count_target:
                        cands = calc_candidates(state, output_str)
                        probs = np.array([x[1] for x in cands])
                        probs = probs / np.sum(probs)
                        idx = np.random.choice(len(probs), p=probs)
                        c = cands[idx][0]
                        print(c)
                        output_str += c
                        return_str += c
                    results.append(return_str)
                    print(results)
        return results

if __name__  == '__main__':
    model_path = sys.argv[1]
    start_str = sys.argv[2]
    append_str_len = int(sys.argv[3])
    rnn = RNNLyricsGen180514(model_path)
    output_str = rnn.run(start_str, append_str_len)
    print(start_str + output_str)