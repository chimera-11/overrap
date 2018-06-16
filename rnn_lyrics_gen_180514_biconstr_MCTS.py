# ---------------------------------------------
#   rnn_lyrics_gen_180514_biconstr_MCTS.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module generates lyrics based on 
#     trained RNN model, taking into account the string
#     in the leading and trailing position.
#     Contrary to the previous approach, which used
#     beam search, this module uses MCTS.
# Usage:
#     python rnn_lyrics_gen_180514_biconstr_MCTS.py <model-path>
#         <leading-phase> <trailing-phase> <char#-to-generate> <#-of-MCTS-sampling>
# Notes:
#     The suffix '180514' indicates the major revision date.
#     The model should match that of rnn_lyrics_train_180514.py.
#     Otherwise errors will occur during model import.
#     The character constraint should be a list of integers [-1..69]
#     each specifying which pivots a character there.
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
import collections
from wordset import Wordset

class ArgRoot:
    def __init__(self):
        self.primer = ''
        self.trailer = ''
        self.char_count = 0
        self.tf_api_wrapper = None
arg_root = ArgRoot()

def count_chars(string):
    return len([x for x in string if x not in [' ', '\n']])

class TFApiWrapper:
    def __init__(self, model_path):
        wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']
        self.wordset = Wordset(wordset)
        self.graph = tf.Graph()
        with self.graph.as_default():
            self.n_inputs = len(self.wordset)     # number of features (= wordset size)
            self.n_steps = 15                     # length of input sequence
            self.n_neurons = 512                  # learning capacity of the network (pretty much arbitrary)
            self.n_layers = 4                     # number of layers
            self.n_outputs = len(self.wordset)    # number of output classes (= wordset size)

            self.X = tf.placeholder(tf.float32, [1, self.n_steps, self.n_inputs])

            cells = []
            for i in range(self.n_layers):
                cell_name = 'cell%d' % i
                cell = tf.contrib.rnn.BasicLSTMCell(num_units=self.n_neurons, name=cell_name)
                cells.append(cell)
            cell = tf.contrib.rnn.MultiRNNCell(cells)
            self.seq_length = tf.placeholder(tf.int32, [None])
            # outputs = [batch_size, max_time, cell.output_size]
            self.init_states = cell.zero_state(1, tf.float32)
            self.outputs, self.states = tf.nn.dynamic_rnn(cell, self.X, dtype=tf.float32,
                sequence_length=self.seq_length, initial_state=self.init_states)
            self.logits = tf.contrib.layers.fully_connected(self.outputs, self.n_outputs, activation_fn=None)

            init = tf.global_variables_initializer()
            config = tf.ConfigProto(device_count={'GPU': 0}) # don't use GPU for generation
            self.sess = tf.Session(config=config)
            self.sess.run(init)
            saver = tf.train.Saver()
            checkpoint_file = os.path.join(model_path, "checkpoint")
            saver_file = os.path.join(model_path, "model-180514.ckpt")
            if not os.path.isfile(checkpoint_file):
                raise EnvironmentError("Couldn't fild the trained data file 'model-180514.ckpt' in the target directory")
            saver.restore(self.sess, saver_file)
    # should be called within 'with self.sess' block
    def _predict_phoneme(self, decomposed_seq, prev_state, temp=1.0):
        input_str = decomposed_seq[-self.n_steps:]
        X_run, seq_len_run = self.wordset.bake_up_run(input_str, self.n_steps)
        X_run = np.reshape(X_run, (-1, self.n_steps, self.n_inputs))
        c, new_state = self.sess.run([self.logits, self.states],
            feed_dict={self.X: X_run, self.seq_length: [seq_len_run], self.init_states: prev_state})
        c = c[0][seq_len_run-1]
        c /= temp
        c = mathutils.softmax(c)
        return c, new_state
    def compute_prob_state(self, full_string):
        state = self.sess.run(self.init_states)
        if len(full_string) == 0:
            return 1.0, state
        decomposed_seq = hangul_decomp.process_data(full_string)
        decomposed_seq = decomposed_seq[:-1]
        processed = ''
        prob = 1.0
        for i in range(len(decomposed_seq) - 1):
            probs, state = self._predict_phoneme(processed, state)
            c = decomposed_seq[i + 1]
            cindex = hangul.phoneme_to_index(c)
            prob *= probs[cindex]
            processed += decomposed_seq[i]
        return prob, state
    def constraint_follow_prob(self, full_string, state):
        decomposed_seq = hangul_decomp.process_data(full_string)
        decomposed_trailer = decomposed_seq[-1] + hangul_decomp.process_data(arg_root.trailer)
        processed = decomposed_seq[:-1]
        prob = 1.0
        for i in range(len(decomposed_trailer) - 1):
            probs, state = self._predict_phoneme(processed, state)
            c = decomposed_trailer[i + 1]
            cindex = hangul.phoneme_to_index(c)
            prob *= probs[cindex]
            processed += decomposed_trailer[i]
        return prob
    def sample_next_char(self, full_string, state, temp=0.5, exclude_space=False):
        return self._sample_next_char(full_string, state, exclude_space)[0:2]
    def _sample_next_char(self, full_string, state, temp=0.5, exclude_space=False):
        decomposed_seq = hangul_decomp.process_data(full_string)
        probs, state = self._predict_phoneme(decomposed_seq, state, temp)
        for i in range(len(hangul.choseongs), len(self.wordset) - 2):
            probs[i] = 0
        if exclude_space:
            probs[68] = 0
        probs[69] = 0
        if decomposed_seq[-1] in [' ', '\n']:
            probs[68] = probs[69] = 0
        probs = np.array(probs)
        probs /= np.sum(probs)
        cidx = np.random.choice(len(probs), p=probs)
        prob = probs[cidx]
        if cidx == 68:
            return ' ', prob, state
        if cidx == 69:
            return '\n', prob, state
        decomposed_seq += hangul.default_wordset[cidx]
        probs, state = self._predict_phoneme(decomposed_seq, state)
        for i in range(len(self.wordset)):
            if i < len(hangul.choseongs) or i >= len(hangul.choseongs) + len(hangul.joongseongs):
                probs[i] = 0
        probs = np.array(probs)
        probs /= np.sum(probs)
        cidx = np.random.choice(len(probs), p=probs)
        decomposed_seq += hangul.default_wordset[cidx]
        prob *= probs[cidx]
        probs, state = self._predict_phoneme(decomposed_seq, state)
        for i in range(len(self.wordset)):
            if i < len(hangul.choseongs) + len(hangul.joongseongs) or i >= 68:
                probs[i] = 0
        probs = np.array(probs)
        probs /= np.sum(probs)
        cidx = np.random.choice(len(probs), p=probs)
        decomposed_seq += hangul.default_wordset[cidx]
        prob *= probs[cidx]
        return hangul_comp.process_data(decomposed_seq[-3:]), pow(prob, 1/3), state
    def sample_to_end(self, full_string, state, prob):
        target_count_remaining = arg_root.char_count - (count_chars(full_string) - count_chars(arg_root.primer))
        while target_count_remaining > 0:
            c, c_prob, state = self._sample_next_char(full_string, state)
            full_string += c
            prob *= c_prob
            target_count_remaining -= count_chars(c)
        return full_string, prob
    def next_prob_state(self, full_string, state, prob, char):
        decomposed_seq = hangul_decomp.process_data(full_string)
        decomposed_char = decomposed_seq[-1] + hangul_decomp.process_data(char)
        processed = decomposed_seq[:-1]
        for i in range(len(decomposed_char) - 1):
            probs, state = self._predict_phoneme(processed, state)
            c = decomposed_char[i + 1]
            cindex = hangul.phoneme_to_index(c)
            prob *= probs[cindex]
            processed += decomposed_char[i]
        return probs, state
class MCTSNode:
    def __init__(self, full_string=''):
        self.parent = None
        self.children = []
        self.nonspace_char_count = 0
        self.prob = 0
        self.char = ''
        self.full_string = full_string
        self.string_prob, self.tf_state = arg_root.tf_api_wrapper.compute_prob_state(full_string)
    def add_child(self, child_char):
        new_child = MCTSNode()
        new_child.parent = self
        new_child.nonspace_char_count = self.nonspace_char_count + (1 if child_char not in [' ', '\n'] else 0)
        new_child.char = child_char
        new_child.full_string = self.full_string + child_char
        new_child.string_prob, new_child.tf_state = \
            arg_root.tf_api_wrapper.next_prob_state(self.full_string, self.tf_state, self.string_prob, child_char)
        self.children.append(new_child)
        return new_child
    def sample_next_char(self, temp=0.5, exclude_space=False):
        return arg_root.tf_api_wrapper.sample_next_char(self.full_string, self.tf_state, temp, exclude_space)
    def run_simulation(self):
        sample = self.sample_to_end()
        print(sample.full_string)
        self.update_prob(sample.prob)
    def update_prob(self, new_prob):
        self.prob = max(self.prob, new_prob)
    def sample_to_end(self):
        full_string, prob = arg_root.tf_api_wrapper.sample_to_end(self.full_string, self.tf_state, self.string_prob)
        prob *= arg_root.tf_api_wrapper.constraint_follow_prob(full_string, self.tf_state)
        Sample = collections.namedtuple('Sample', ['full_string', 'prob'])
        return Sample(full_string=full_string, prob=prob)
    def children_count_max(self):
        if self.nonspace_char_count < arg_root.char_count:
            last_char = self.full_string[-1]
            if last_char in [' ']:
                return 11172 # hangul (11172)
            else:
                return 11173 # hangul (11172) + space
        if self.nonspace_char_count == arg_root.char_count:
            last_char = self.full_string[-1]
            if last_char in [' ']:
                return 0
            else:
                return 1 # space
        return 0

def mcts_core(root, number_of_iterations=1000):
    # I. MCTS loop
    for iteration in range(1, number_of_iterations + 1):
        # 1. selection
        node = root
        while True:
            if node.children_count_max() == 0:
                # if we reach an already explored terminal node,
                # discard it and start again
                node = root
            probs = [0] * len(node.children)
            for i in range(len(node.children)):
                probs[i] = node.children[i].prob
            #if len(probs) > 0:
                probs /= max(probs) / 3
            if len(node.children) < node.children_count_max():
                probs = list(probs)
                probs.append(0) # indicates that we expand on this node
            probs = mathutils.softmax(probs) # some kind of weighting
            idx = np.random.choice(len(probs), p=probs)
            if idx == len(node.children): # reached the node to expand
                break
            node = node.children[idx]
        # 2. expansion
        exclude_space = ' ' in [x.char for x in node.children]
        while True:
            c = node.sample_next_char(temp=1.0, exclude_space=exclude_space)[0]
            if c not in [x.char for x in node.children]:
                break
            print('argggg @ %s' % c)
        node_new = node.add_child(c)
        # 3. simulation
        for _ in range(3):
            node_new.run_simulation()
        # 4. backpropagation
        node = node_new.parent
        while node != None:
            node.update_prob(node_new.prob)
            node = node.parent
        print('iteration %d end' % iteration)
    # II. Select best node
    node = root
    while len(node.children) > 0:
        most_probable_child = max(node.children, key=lambda x: x.prob)
        if node.prob > most_probable_child.prob:
            break
        node = most_probable_child
    return node.sample_to_end().full_string

def mcts(primer, trailer, char_count, model_path):
    arg_root.primer = primer
    arg_root.trailer = trailer
    arg_root.char_count = char_count
    arg_root.tf_api_wrapper = TFApiWrapper(model_path)
    root = MCTSNode(full_string=primer)
    return mcts_core(root)

model_path = sys.argv[1]
primer = '사랑'
trailer = '사람'
char_count = 6
line = mcts(primer, trailer, char_count, model_path)
print(line)
