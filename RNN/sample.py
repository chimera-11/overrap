#!/usr/bin/python # -*- coding: utf8 -*-

from __future__ import print_function
import tensorflow as tf

import argparse
import os
import re
import random
from six.moves import cPickle

from model import Model

from six import text_type


def main():
    tf.reset_default_graph()
    parser = argparse.ArgumentParser(
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--save_dir', type=str, default='save_rap_balad',
                        help='model directory to store checkpointed models')
    parser.add_argument('-n', type=int, default=20,
                        help='number of characters to sample')
    parser.add_argument('--prime', type=text_type, default=u'',
                        help='prime text')
    parser.add_argument('--sample', type=int, default=1,
                        help='0 to use max at each timestep, 1 to sample at '
                             'each timestep, 2 to sample on spaces')

    args = parser.parse_args()
    num = 0
    word = ' '
    string = ''
    while word != '-1' :
        tf.reset_default_graph()
        word = input("Input a word to get more sentence or -1 restart to 0\n")
        if word == '-1' :
            break
        elif word == '0' :
            string = ''
            num = 0
            args.prime = ''
        else :
            args.prime = args.prime + ' ' + word
            if num%2 == 0:
                str_len = random.randint(10, 15)
                args.prime = sample(args, str_len)
                print(string + args.prime)

            else :
                str_len = 20 + random.randint(0, 2)
                string = string + sample(args, str_len)
                args.prime = ''
                print(string)
            num += 1
            


def sample(args, str_len):
    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
        chars, vocab = cPickle.load(f)
    model = Model(saved_args, training=False)
    with tf.Session() as sess:
        result = ''
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            string = model.sample(sess, chars, vocab, args.n, args.prime, args.sample)
            for x in string :
                if (x == ' ') :
                    if (len(result) > str_len) :
                       # print(result)
                        return result
                result = result + x
                
                
if __name__ == '__main__':
    main()
