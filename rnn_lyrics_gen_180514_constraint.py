# ---------------------------------------------
#   rnn_lyrics_gen_180514_constraint.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module generates lyrics based on 
#     trained RNN model, adhering to the given
#     consonant/vowel pivot constraint.
# Usage:
#     python rnn_lyrics_gen_180514_constraint.py <model-path> <priming-phrase> <character-constraint>
# Notes:
#     The suffix '180514' indicates the major revision date.
#     The model should match that of rnn_lyrics_train_180514.py.
#     Otherwise errors will occur during model import.
#     The character constraint should be a list of integers [-1..69]
#     each specifying which pivots a character there.
#     Here, -1 means a position do not have any constraints.
#     As the algorithm runs brute force (beam search) using
#     the softmax probabilities, it is recommended to keep the
#     length of the character constraint below 7.
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


class RNNLyricsGen180514Constraint:
    def __init__(self, model_path):
        self.model_path = model_path
        wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']
        self.wordset = Wordset(wordset)
    # pruning_prob: 평균 확률이 더 좋은 값이 알려져 있을때,
    #  그 확률보다 잘 나오지 않을 것은 검색하지 않으려면 지정
    #  (run 함수의 반환값처럼 조화평균이어야 함)
    def run(self, start_str, char_constraint, pruning_prob=0):
        with tf.Graph().as_default():       # use local graph, prevent parameter duplicate issue
            model_path = self.model_path
            wordset = self.wordset

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

            start_str_decomp = hangul_decomp.process_data(start_str)
            output_str = start_str_decomp
            return_str = ''
            seq_len_default = 30

            self.best_seq = []
            self.best_prob = 0
            self.pruning_prob = np.power(pruning_prob, len(char_constraint)) if pruning_prob > 0 else 0

            config = tf.ConfigProto(
                    device_count = {'GPU': 0} # don't use GPU for generation
                )
            with tf.Session(config=config) as sess:
                init.run()
                saver = tf.train.Saver()
                checkpoint_file = os.path.join(model_path, "checkpoint")
                saver_file = os.path.join(model_path, "model-180514.ckpt")
                if not os.path.isfile(checkpoint_file):
                    raise EnvironmentError("Couldn't fild the trained data file 'model-180514.ckpt' in the target directory")
                saver.restore(sess, saver_file)
                def dfs(depth, seq, prob, prev_state):
                    if prob < self.best_prob or prob < self.pruning_prob:
                        return # early pruning
                    if depth == len(char_constraint):
                        if prob > self.best_prob:
                            self.best_seq, self.best_prob = seq, prob
                        return
                    # beam search (branching factor = 4)
                    input_str = seq[-seq_len_default:]
                    X_run, seq_len_run = wordset.bake_up_run(input_str, seq_len_default)
                    X_run = np.reshape(X_run, (-1, n_steps, n_inputs))
                    c, state = sess.run([logits, states],
                        feed_dict={X: X_run, seq_length: [seq_len_run], init_states: prev_state})
                    c = c[0][seq_len_run-1]
                    c = mathutils.softmax(c)
                    if char_constraint[depth] == -1:
                        id_prob_tuple = [(i, c[i]) for i in range(len(wordset))]
                        id_prob_tuple = sorted(id_prob_tuple, key=lambda x: x[1], reverse=True)
                        branching_factor = 4
                        i = 0
                        child_cnt = 0
                        while i < len(wordset) and child_cnt < branching_factor:
                            char_idx, char_prob = id_prob_tuple[i]
                            char = wordset.wordset[char_idx]
                            if hangul.adjacency_possible(seq[-1], char):
                                dfs(depth + 1, seq + char, prob * char_prob, state)
                                child_cnt += 1
                            i += 1
                        if seq[-1] != ' ' and hangul.adjacency_possible(seq[-1], ' '):
                            space_idx = wordset.char_to_index(' ')
                            space_prob = c[space_idx]
                            dfs(depth + 1, seq + ' ', prob * space_prob, state)
                    else:
                        fixed_char_idx = char_constraint[depth]
                        fixed_char = wordset.wordset[fixed_char_idx]
                        if hangul.adjacency_possible(seq[-1], fixed_char):
                            dfs(depth + 1, seq + fixed_char, prob * c[fixed_char_idx], state)
                dfs(0, start_str_decomp, 1, sess.run(cell.zero_state(1, tf.float32)))
                if __name__ == '__main__':
                    if self.best_prob == 0:
                        self.best_seq = 'Failed to generate'
                    else:
                        print(self.best_prob)
                return_str = self.best_seq
        return hangul_comp.process_data(return_str), np.power(self.best_prob, 1 / len(char_constraint))

if __name__  == '__main__':
    model_path = sys.argv[1]
    start_str = sys.argv[2]
    rnn = RNNLyricsGen180514Constraint(model_path)
    char_constraint = [-1] * 9
    char_constraint[-2] = rnn.wordset.char_to_index(hangul.joongseongs[hangul.get_vowel_index('에')])
    output_str, avg_prob = rnn.run(start_str, char_constraint)
    print(list(output_str))
    output_str = output_str.replace('\n', ' ').replace('  ', ' ')
    print(output_str)
    print(avg_prob)