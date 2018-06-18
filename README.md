# overrap
overrap은 한국어 랩 가사 생성 AI입니다.

LSTM RNN을 이용해 가사를 학습하여 생성하며, 생성된 가사 중에서 라임이 가장 잘 맞는 것을 고릅니다.
생성되는 가사의 형태는 10-12글자 4줄이며, 말단 모음은 일치하는 계열이 맞도록 조정해 생성합니다.
첫째 줄과 셋째 줄의 첫 단어는 word2vec을 이용해 유사한 단어를 뽑아 pivot으로써 배정합니다.

이때, pivot으로 고정된 것을 고려하기 위해 Ending Modulation이라는 테크닉을 사용합니다.
Ending Modulation이란 RNN의 확률 모델을 이용해 beam search를 수행하는 방식입니다.
둘째 줄의 마지막 5글자를 생성할 때는 셋째 줄의 시작부분에 있는 word2vec pivot을 고려해야 문맥이 자연스럽게 이어지기 때문에,
해당 부분을 생성한 후 뒤이어 셋째 줄의 시작부분에 있는 단어가 올 확률이 얼마나 되는지를 고려합니다.
이를 응용하여, 모든 라인이 끝날 때는 pivot이 없더라도 개행 문자가 바로 다음에 올 확률이 얼마나 되는지를 고려하여 생성함으로써
줄의 마지막 부분 마무리를 자연스럽게 만들어줍니다.

# overrap (English)
overrap is an AI application that generates rap lyrics in Korean.

For modeling the lyrics, we use LSTM RNN. 
Among the generated lyrics candidates, we select the one which rhymes best with the previous line.
The lyrics will be a four-line one, with each line having 10-12 characters.
We use word2vec to sample two words that are similar in meaning,
and put each of them as the first word (pivot) of the first and the third line respectively.

Here we use a technique called Ending Modulation to take the pivots into consideration.
This technique performs a beam search using the probability model of the RNN.
When a pivot is introduced to RNN during lyrics generation, the context gets awkward
as the RNN had no knowledge of the upcoming pivot word.
In order to address this problem, we evaluate each candidate by letting the RNN
evaluate the probability of the pivot following a lyrics line.
This is applied to the generation of the ending of the second line, which has a pivot following on the third line.
We also apply this technique for finalizing each line even if that line does not have a pivot following,
which makes the endings more natural.

# 생성 예시 1
돌아간대도 나를 보고 싶어

나는 바보야 너와 함께 있어

돌아가잔 말을 하고 싶어

오늘도 나를 사랑하는 걸


# 생성 예시 2
난장이 오늘 밤이 내려요

나를 아프게 하지마 그래서요

아주작은 시간이 좋겠어요

시간이 지나가는 사람이죠

# 생성 예시 3
생각하지는 않아요 사랑해

너를 사랑하는 시간이 있는데

마지막날은 아니라고 말해

너무 아파하지 말아야해
