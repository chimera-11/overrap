from char_gen_base import CharGenBase
from rnn_lyrics_gen import RNNLyricsGen
from rnn_lyrics_gen_180514 import RNNLyricsGen180514

class CharGenRNN(CharGenBase):
    def __init__(self, model_path):
        self.rnn = RNNLyricsGen(model_path)
    def generate(self, input_str, out_len):
        return self.rnn.run(input_str, out_len)

class CharGenRNN180514(CharGenBase):
    def __init__(self, model_path):
        self.rnn = RNNLyricsGen180514(model_path)
    def generate(self, input_str, out_len):
        return self.rnn.run(input_str, out_len)