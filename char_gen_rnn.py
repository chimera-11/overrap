from char_gen_base import CharGenBase
from rnn_lyrics_gen import RNNLyricsGen

class CharGenRNN(CharGenBase):
    def __init__(self, model_path):
        self.rnn = RNNLyricsGen(model_path)
    def generate(self, input_str, out_len):
        return self.rnn.run(input_str, out_len)