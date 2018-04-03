import urllib.request
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

_caps = DesiredCapabilities.PHANTOMJS
_caps["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
_my_driver = webdriver.PhantomJS(service_args=['--proxy-type=none'])
def download(url):
    _my_driver.get(url)
    return_val = _my_driver.page_source
    return return_val
def querySong(id, myfile):
    url = 'https://www.melon.com/song/detail.htm?songId=%s' % (id)
    data = download(url)
    regex = re.compile(r'<div class="lyric" id="d_video_summary">.*\r*\n[ \t]*([^\r\n]+)')
    lyrics_list = regex.findall(data)
    if not lyrics_list:
        #nolyrics_list = re.compile(r'<div class="lyric_none">').findall(data)
        #if nolyrics_list:
            #print('Lyrics not available yet')
        #else:
            #print('Cannot parse lyrics HTML')
        return
    lyrics = lyrics_list[0]
    regex = re.compile(r'(.+?)<[Bb][Rr]>')
    lines = regex.findall(lyrics)    
    myfile.write(id + '\n')
    for line in lines:
        myfile.write(line + '\n')
    myfile.write('\n')

url_base = 'https://www.melon.com/genre/song_list.htm?gnrCode=GN0300#params%5BgnrCode%5D=GN0300&params%5BdtlGnrCode%5D=&params%5BorderBy%5D=NEW&params%5BsteadyYn%5D=N&po=pageObj&startIndex='

for i in range(1, 1000, 50):
    with open("test" + str(i) + ".txt", "a", encoding='UTF8') as myfile:
        text = download(url_base + str(i))
        regex = re.compile(r"javascript:melon\.link\.goSongDetail\('(\d+)'\)")
        nums = regex.findall(text)
        for j in nums:
            print("Song number " + str(j) + " processed")
            querySong(j, myfile)
