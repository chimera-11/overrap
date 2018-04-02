import urllib.request
import re

def download(url):
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
    )
    return urllib.request.urlopen(req).read().decode('utf-8')
def querySong(id):
    url = 'https://www.melon.com/song/detail.htm?songId=%s' % (id)
    data = download(url)
    regex = re.compile(r'<div class="lyric" id="d_video_summary">.*\r*\n[ \t]*([^\r\n]+)')
    lyrics_list = regex.findall(data)
    if not lyrics_list:
        nolyrics_list = re.compile(r'<div class="lyric_none">').findall(data)
        if nolyrics_list:
            print('Lyrics not available yet')
        else:
            print('Cannot parse lyrics HTML')
        return
    lyrics = lyrics_list[0]
    regex = re.compile(r'(.+?)<BR>')
    lines = regex.findall(lyrics)
    for line in lines:
        print(line)

url = 'https://www.melon.com/genre/song_list.htm?gnrCode=GN0300#params%5BgnrCode%5D=GN0300&params%5BdtlGnrCode%5D=&params%5BorderBy%5D=NEW&params%5BsteadyYn%5D=N&po=pageObj&startIndex=1'
text = download(url)
regex = re.compile(r"javascript:melon\.link\.goSongDetail\('(\d+)'\)")
nums = regex.findall(text)
for i in nums:
    print(i)
    querySong(i)
    print('')
