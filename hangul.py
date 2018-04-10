def is_hangul_char(c):
    c = ord(c)
    return c >= 0xAC00 and c <= 0xD7A3

choseongs = ['\u1100', '\u1101', '\u1102', '\u1103', '\u1104', '\u1105', '\u1106', '\u1107', '\u1108', '\u1109', '\u110A', '\u110B', '\u110C', '\u110D', '\u110E', '\u110F', '\u1110', '\u1111', '\u1112']
joongseongs = [ "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
jongseongs = ['+', '\u3131', '\u3132', '\u3133', '\u3134', '\u3135', '\u3136', '\u3137', '\u3139', '\u313A', '\u313B', '\u313C', '\u313D', '\u313E', '\u313F', '\u3140', '\u3141', '\u3142', '\u3144', '\u3145', '\u3146', '\u3147', '\u3148', '\u314A', '\u314B', '\u314C', '\u314D', '\u314E']
def decompose_hangul(c):
    # 한글유니코드값 = 0xAC00 + ( (초성순서 * 21) + 중성순서 ) * 28 + 종성순서
    c = ord(c) - 0xAC00
    jongseong = c % 28
    c //= 28
    joongseong = c % 21
    c //= 21
    choseong = c
    return choseongs[choseong] + joongseongs[joongseong] + jongseongs[jongseong]

def is_choseong(c):
    return c in choseongs
def is_joongseong(c):
    return c in joongseongs
def is_jongseong(c):
    return c in jongseongs
def is_hangul_phoneme(c):
    return c in choseongs or c in joongseongs or c in jongseongs

def find_element_in_list(element, list_element):
    try:
        index = list_element.index(element)
        return index
    except ValueError:
        return -1

def compose_from_index(choseong_index, joongseong_index, jongseong_index):
    c = choseong_index
    c *= 21
    c += joongseong_index
    c *= 28
    c += jongseong_index
    c += 0xAC00
    return chr(c)

def try_compose(choseong, joongseong, jongseong):
    choseong = str(choseong)
    joongseong = str(joongseong)
    jongseong = str(jongseong)
    choseong_index = find_element_in_list(choseong, choseongs)
    joongseong_index = find_element_in_list(joongseong, joongseongs)
    jongseong_index = find_element_in_list(jongseong, jongseongs)
    if -1 in [choseong_index, joongseong_index, jongseong_index]:
        return [False, choseong + joongseong + jongseong]
    return [True, compose_from_index(choseong_index, joongseong_index, jongseong_index)]