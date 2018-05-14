#!/usr/bin/python # -*- coding: utf8 -*-

from __future__ import print_function
import tensorflow as tf

import argparse
import os
import re
import random
from six.moves import cPickle

from RNN.model import Model
#from model import Model

from six import text_type

class Sampler:
    def __init__(self, model_path='RNN\\save_balad'):
        parser = argparse.ArgumentParser(
                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument('--save_dir', type=str, default=model_path,
                            help='model directory to store checkpointed models')
        parser.add_argument('-n', type=int, default=20,
                            help='number of characters to sample')
        parser.add_argument('--prime', type=text_type, default=u'',
                            help='prime text')
        parser.add_argument('--sample', type=int, default=1,
                            help='0 to use max at each timestep, 1 to sample at '
                                'each timestep, 2 to sample on spaces')
        parser.add_argument('--numlines', type=int, default=8,
                            help='number of lines to be generated. not used within '
                                'this module')
        args = parser.parse_args()
        self._args = args

    def interactive_loop(self):
        num = 0
        word = ' '
        string = ''
        while word != '-1' :
            #tf.reset_default_graph()
            word = input("Input a word to get more sentence or -1 restart to 0\n")
            if word == '-1' :
                break
            elif word == '0' :
                string = ''
                num = 0
                self.clear_prime_text()
            else :
                self._args.prime = self._args.prime + ' ' + word
                if num%2 == 0:
                    str_len = random.randint(10, 15)
                    self.set_prime_text(self.sample(str_len))
                    print(string + self.get_prime_text())

                else :
                    str_len = 20 + random.randint(0, 2)
                    string = string + self.sample(str_len)
                    self.clear_prime_text()
                    print(string)
                num += 1
    def set_prime_text(self, prime_text):
        self._args.prime = str(prime_text)
    def append_prime_text(self, append_text):
        self._args.prime += str(append_text)
    def clear_prime_text(self):
        self._args.prime = ''
    def get_prime_text(self):
        return self._args.prime

    def sample(self, str_len, return_prefix_prime=True):
        tf.reset_default_graph()
        args = self._args
        with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
            saved_args = cPickle.load(f)
        with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
            chars, vocab = cPickle.load(f)
        model = Model(saved_args, training=False)
        config = tf.ConfigProto(
                    device_count = {'GPU': 0} # don't use GPU for generation
                )
        with tf.Session(config=config) as sess:
            result = ''
            tf.global_variables_initializer().run()
            saver = tf.train.Saver(tf.global_variables())
            ckpt = tf.train.get_checkpoint_state(args.save_dir)
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                string = model.sample(sess, chars, vocab, args.n, \
                    args.prime, args.sample, return_prefix_prime=return_prefix_prime)
                for x in string :
                    if (x == ' ') :
                        if (len(result) > str_len) :
                        # print(result)
                            return result
                    result = result + x
                    
                    
if __name__ == '__main__':
    s = Sampler()
    s.interactive_loop()
