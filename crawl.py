import urllib.request
import re
import time
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def download_dynamic(url, wait_sec):
    _my_driver.get(url)
    time.sleep(wait_sec)
    return_val = _my_driver.page_source
    return return_val
def download(url):
    req = urllib.request.Request(
        url, 
        data=None, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
    )
    return urllib.request.urlopen(req).read().decode('utf-8')
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
        return False
    lyrics = lyrics_list[0]
    regex = re.compile(r'(.+?)<[Bb][Rr]>')
    lines = regex.findall(lyrics)
    #myfile.write(id + '\n')
    regex_backup = re.compile(re.escape('<br>'), re.IGNORECASE)
    for line in lines:
        myfile.write(regex_backup.sub('', line) + '\n')
    myfile.write('\n')
    return True

url_base_hiphop = 'https://www.melon.com/genre/song_list.htm?gnrCode=GN0300#params%5BgnrCode%5D=GN0300&params%5BdtlGnrCode%5D=&params%5BorderBy%5D=NEW&params%5BsteadyYn%5D=N&po=pageObj&startIndex='
url_base_balad = 'https://www.melon.com/genre/song_list.htm#params%5BgnrCode%5D=GN0100&params%5BdtlGnrCode%5D=&params%5BorderBy%5D=NEW&params%5BsteadyYn%5D=N&po=pageObj&startIndex='
url_base_dance = 'http://www.melon.com/genre/song_list.htm?gnrCode=GN0200#params%5BgnrCode%5D=GN0200&params%5BdtlGnrCode%5D=&params%5BorderBy%5D=NEW&params%5BsteadyYn%5D=N&po=pageObj&startIndex='
url_base = url_base_balad

_caps = DesiredCapabilities.PHANTOMJS
_caps["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
_my_driver = webdriver.PhantomJS(service_args=['--proxy-type=none'])

i_start = int(sys.argv[1])      # inclusive
i_end = int(sys.argv[2])        # exclusive
os.chdir(sys.argv[3])

def run_download(i_start, i_end):
    for k in range(i_start, i_end):
        i = 50 * k + 1
        text = download_dynamic(url_base + str(i), 7)
        regex = re.compile(r"javascript:melon\.link\.goSongDetail\('(\d+)'\)")
        nums = regex.findall(text)
        yet_to_succeed = True
        while yet_to_succeed:
            yet_to_succeed = False
            for j in nums:
                try:
                    filename = str(j) + ".txt"
                    if os.path.isfile(filename) and os.stat(filename).st_size > 0:
                        print("Song number " + str(j) + " already exists; skipping")
                        continue
                    with open(filename, "w", encoding='UTF8') as myfile:
                        result = querySong(j, myfile)
                    if result:
                        print("Song number " + str(j) + " processed")
                    else:
                        print("Song number " + str(j) + " has no lyrics available yet")
                except Exception:
                    yet_to_succeed = True
                    break

run_download(i_start, i_end)

_my_driver.close()
_my_driver.quit()
