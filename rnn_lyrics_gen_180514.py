# ---------------------------------------------
#   rnn_lyrics_gen_180514.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module generates lyrics based on 
#     trained RNN model.
# Usage:
#     python rnn_lyrics_gen_180514.py <model-path> <priming-phrase> <#-of-char-to-append>
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
            outputs, states = tf.nn.dynamic_rnn(cell, X,
                dtype=tf.float32, sequence_length=seq_length, initial_state=init_states)

            logits = tf.contrib.layers.fully_connected(outputs, n_outputs, activation_fn=None)
            #xentropy = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)

            init = tf.global_variables_initializer()

            output_count_target = len(start_str) + append_count
            seq_len_default = n_steps

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
                    output_str = hangul_decomp.process_data(start_str)
                    return_str = ''
                    state = sess.run(cell.zero_state(1, tf.float32))
                    for i in range(len(output_str)):
                        input_str = output_str[0:i]
                        if len(input_str) < 5:
                            continue
                        if len(input_str) > seq_len_default:
                            input_str = input_str[-seq_len_default:]
                        X_run, seq_len_run = wordset.bake_up_run(input_str, seq_len_default)
                        X_run = np.reshape(X_run, (-1, n_steps, n_inputs))
                        c, state = sess.run([logits, states],
                            feed_dict={X: X_run, seq_length: [seq_len_run], init_states: state})
                    while len(hangul_comp.process_data(output_str)) < output_count_target \
                        or not hangul.is_complete(output_str) \
                        or (output_str[-1] != ' ' and output_str[0] != '\n'):
                        # predict next character
                        input_str = output_str[-seq_len_default:]
                        X_run, seq_len_run = wordset.bake_up_run(input_str, seq_len_default)
                        X_run = np.reshape(X_run, (-1, n_steps, n_inputs))
                        #print(np.shape(X_run))
                        c, state = sess.run([logits, states],
                            feed_dict={X: X_run, seq_length: [seq_len_run], init_states: state})
                        #print(np.shape(c))
                        c = c[0][seq_len_run-1]
                        b = output_str[-1]
                        if hangul.is_choseong(b):
                            option = "choseong"
                        elif hangul.is_joongseong(b):
                            option = "joongseong"
                        elif hangul.is_jongseong(b):
                            option = "jongseong"
                        else:
                            option = "not_hangul"
                        c /= 0.5
                        c_sample = wordset.sample_context_aware(mathutils.softmax(c), option)
                        #c_sample = wordset.sample_from(mathutils.softmax(c))
                        output_str += c_sample
                        return_str += c_sample
                    results.append(hangul_comp.process_data(return_str))
                    print(results)
        return results

if __name__  == '__main__':
    model_path = sys.argv[1]
    start_str = sys.argv[2]
    append_str_len = int(sys.argv[3])
    rnn = RNNLyricsGen180514(model_path)
    output_str = rnn.run(start_str, append_str_len)
    print(start_str + output_str)