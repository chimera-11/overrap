# ---------------------------------------------
#   rnn_lyrics_train_180514.py
#   Copyright (C) 2018 Ahn Byeongkeun
# ---------------------------------------------
# Description:
#     This module traines RNN model to generate lyrics.
#     The model is a stacked collection of LSTM,
#     which gets its input in the form of one-hot vector.
#     The one-hot vectors are generated from character
#     decomposition, that is, for example,
#         '가' -> 'ㄱㅏ+',
#         '환' -> 'ㅎㅘㄴ'.
#     This subcharacter embedding reduces the complexity
#     of the network compared to character-level embedding.
# Usage:
#     python rnn_lyrics_train-180514.py <corpus-folder-path> <[optional]testset-folder-path>
# Options:
#     --test          compute loss of the specified testset
#                     using the trained model
#     --nogpu         forces CPU training even when GPU
#                     acceleration is available
# Notes:
#     The suffix '180514' indicates the major revision date.
#     In the corpus folder, all files with .txt extension
#     are incorporated into the training set.
#     Also note that they should be UTF-8 encoded.

import tensorflow as tf
import sys
import hangul
import numpy
import os
from LyricsDataset180514 import LyricsDataset180514

import cProfile

def run():
    wordset = hangul.choseongs + hangul.joongseongs + hangul.jongseongs + [' ', '\n']

    n_inputs = len(wordset)     # number of features (= wordset size)
    n_steps = 30                # length of input sequence
    n_neurons = 512             # learning capacity of the network (pretty much arbitrary)
    n_layers = 4                # number of layers
    n_outputs = len(wordset)    # number of output classes (= wordset size)

    learning_rate = 0.001
    is_test = '--test' in sys.argv
    is_nogpu = '--nogpu' in sys.argv
    #if is_test: learning_rate = 0

    X = tf.placeholder(tf.float32, [None, n_steps, n_inputs], name="X")
    y = tf.placeholder(tf.int32, [None, n_steps, n_outputs], name="y")

    cells = []
    for i in range(n_layers):
        cell_name = 'cell%d' % i
        cell = tf.contrib.rnn.BasicLSTMCell(num_units=n_neurons, name=cell_name)
        cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=0.5)
        cells.append(cell)
    cell = tf.contrib.rnn.MultiRNNCell(cells)
    seq_length = tf.placeholder(tf.int32, [None])
    # outputs = [batch_size, max_time, cell.output_size]
    outputs, _ = tf.nn.dynamic_rnn(cell, X, dtype=tf.float32, sequence_length=seq_length)

    logits = tf.contrib.layers.fully_connected(outputs, n_outputs, activation_fn=None)
    #xentropy = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)
    xentropy = tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=logits)
    loss = tf.reduce_mean(xentropy)
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    training_op = optimizer.minimize(loss)
    #training_op = loss
    #correct = tf.nn.in_top_k(logits, y, 1)
    #accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))
    init = tf.global_variables_initializer()

    X_test = []
    y_test = []

    n_epochs = 100
    batch_size = 1000


    model_path = sys.argv[1]
    data_path = sys.argv[2] if is_test else sys.argv[1]
    lyrics_dataset = LyricsDataset180514(path=data_path, wordset=wordset, seq_len_default=n_steps, seq_len_min=5)
    if is_test:
        n_epochs = 1
    
    if is_nogpu:
        config = tf.ConfigProto(device_count = {'GPU': 0})
    else:
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9)
        config = tf.ConfigProto(gpu_options=gpu_options)
    with tf.Session(config=config) as sess:
    #with tf.Session() as sess:
        #file_writer = tf.summary.FileWriter('..\\tensorflow-logs', sess.graph)
        #merged = tf.summary.merge_all()

        init.run()
        saver = tf.train.Saver()
        checkpoint_file = os.path.join(model_path, "checkpoint")
        saver_file = os.path.join(model_path, "model-180514.ckpt")
        if os.path.isfile(checkpoint_file):
            saver.restore(sess, saver_file)
        elif is_test:
            raise EnvironmentError('No model found to test against')
        lyrics_dataset.reset()
        prev_counter = 0
        while lyrics_dataset.counter < n_epochs:
            total_loss = 0
            i = 0
            while lyrics_dataset.counter == prev_counter:
                i += 1
                X_batch, y_batch, seq_len_batch = lyrics_dataset.next_batch(batch_size)
                X_batch = numpy.reshape(X_batch, (-1, n_steps, n_inputs))
                #X_batch = X_batch.reshape((-1, n_steps, n_inputs))
                if not is_test:
                    #_, loss_val = sess.run([training_op, loss], feed_dict={X: X_batch, y:y_batch, seq_length: seq_len_batch})
                    sess.run(training_op, feed_dict={X: X_batch, y:y_batch, seq_length: seq_len_batch})
                    loss_val = sess.run(loss, feed_dict={X: X_batch, y:y_batch, seq_length: seq_len_batch})
                    #summary = sess.run(merged)
                    #file_writer.add_summary(summary, i)
                else:
                    loss_val = sess.run(loss, feed_dict={X: X_batch, y:y_batch, seq_length: seq_len_batch})
                    print('testing')
                #print(loss_val)
                total_loss += loss_val
                if not is_test and i % 50 == 0:
                    try:
                        save_path = saver.save(sess, saver_file)
                    except Exception as e:
                        print(e)
                    print('Step ' + str(i) + ', Current loss =', '{:.3f}'.format(loss_val), 'saved')
                else:
                    print('Step ' + str(i) + ', Current loss =', '{:.3f}'.format(loss_val))
            print('Total current loss =', '{:.3f}'.format(total_loss / i))
            if not is_test:
                try:
                    save_path = saver.save(sess, saver_file)
                except Exception as e:
                    print(e)
            prev_counter += 1
run()