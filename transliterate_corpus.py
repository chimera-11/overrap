#import transliteration
#from transliteration import Transliteration

#tl = Transliteration()
#tl_ret = tl.run(b'kakao').decode('utf-8')
#print(tl_ret)

from korean.cmuToKorean import CMUToKorean

def get_pronunciation(word):
    with open('cmudict-0.7b.txt', 'r', encoding='utf8') as cmudict:
        line = cmudict.readline()
        while line:
            line = cmudict.readline()
            tokens = line.split()
            if tokens[0] == word.upper():
                return ' '.join(tokens[1:])
    return ''

def read_word(word_english, verbose=False):
    word_pronunciation = get_pronunciation(word_english)

    if verbose:
        print('pronunciation symbols: ' + word_pronunciation)
    result = CMUToKorean.convert(word_english, word_pronunciation)

    if verbose:
        for v in result:
            print(v)
    return result[0]

def read_sentence(sentence):
    words = sentence.split()
    read_words = []
    for word in words:
        read_words.append(read_word(word))
    return ' '.join(read_words)

print(read_sentence('Oh be a fine girl kiss me what'))
read_word('What', verbose=True)
