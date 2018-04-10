import tensorflow as tf
import sys
import hangul
import hangul_comp
import hangul_decomp
import numpy as np
import os
from lyrics_dataset import LyricsDataset
from wordset import Wordset

model_path = sys.argv[1]
start_str = sys.argv[2]

wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']
wordset = Wordset(wordset)

def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

n_inputs = len(wordset)     # number of features (= wordset size)
n_steps = 1                # length of input sequence
n_neurons = 128             # learning capacity of the network (pretty much arbitrary)
n_outputs = len(wordset)    # number of output classes (= wordset size)

X = tf.placeholder(tf.float32, [None, n_steps, n_inputs], name="X")
seq_length = tf.placeholder(tf.int32)
cell = tf.contrib.rnn.GRUCell(num_units=n_neurons)
outputs, states = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32, sequence_length=seq_length)

logits = tf.contrib.layers.fully_connected(states, n_outputs, activation_fn=None)
init = tf.global_variables_initializer()

output_str = hangul_decomp.process_data(start_str)
output_count_target = 100

config = tf.ConfigProto(
        device_count = {'GPU': 0}
    )
with tf.Session(config=config) as sess:
    init.run()
    saver = tf.train.Saver()
    checkpoint_file = os.path.join(model_path, "checkpoint")
    saver_file = os.path.join(model_path, "model.ckpt")
    if not os.path.isfile(checkpoint_file):
        raise EnvironmentError("Couldn't fild the trained data file 'model.ckpt' in the target directory")
    saver.restore(sess, saver_file)
    for _ in range(output_count_target):
        # predict next character
        input_str = output_str[-30:]
        X_run, seq_len_run = wordset.bake_up_run(input_str, 30)
        X_run = np.reshape(X_run, (-1, n_steps, n_inputs))
        c = sess.run(logits, feed_dict={X: X_run, seq_length: seq_len_run})
        c = c[-1]
        b = output_str[-1]
        if hangul.is_choseong(b):
            option = "choseong"
        elif hangul.is_joongseong(b):
            option = "joongseong"
        elif hangul.is_jongseong(b):
            option = "jongseong"
        else:
            option = "not_hangul"
        output_str += wordset.sample_context_aware(softmax(c), option)
print(hangul_comp.process_data(output_str))
