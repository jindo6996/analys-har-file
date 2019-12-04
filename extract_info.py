import json
import time

from haralyzer import HarParser
import re
from selenium import webdriver
from browsermobproxy import Server
from youtube_transcript_api import YouTubeTranscriptApi


def check_url(url):
    ok = re.match(r".*googlevideo\.com", url)
    return ok


def get_data_length(entry):
    response = entry.get('response', 'not found response')
    content = response.get('content', 'not found content')
    size = content.get('size', 'not found size')
    return size


def get_time_to_download(entry):
    timings = entry.get('timings', 'not found timings')
    receive = timings.get('receive', 'not found receive')
    print(receive)
    return receive

def get_total_data_content(path_har):
    with open(path_har, 'r') as f:
        har_parser = HarParser(json.loads(f.read()))

    print(har_parser.hostname)

    i = 0
    total_download = 0
    time_to_download_total = 0
    for e in har_parser.har_data.get('entries', 'not found'):
        request = e.get('request', 'not found request')
        url = request.get('url', 'not found url')
        if check_url(url):
            i = i + 1
            data = get_data_length(e)
            if data >= 0:
                total_download += data
                time_to_download_total += get_time_to_download(e)

            print("url: {0}\n".format(url))
    print("\n\n\nTotal download: ", total_download)
    print("\n\n\nTotal receive time: ", time_to_download_total)
        # returns True for each


class CreateHar(object):
    """create HTTP archive file"""

    def __init__(self, mob_path):
        self.browser_mob = mob_path
        self.server = self.driver = self.proxy = None

    @staticmethod
    def __store_into_file(title, result):
        har_file = open('./results/'+title + '.har', 'w')
        har_file.write(str(result))
        har_file.close()

    def __start_server(self):
        self.server = Server(self.browser_mob)
        self.server.start()
        self.proxy = self.server.create_proxy()

    def __start_driver(self):
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(self.proxy.selenium_proxy())
        self.driver = webdriver.Firefox(firefox_profile=profile)

    def start_all(self):
        self.__start_server()
        self.__start_driver()

    def create_har(self, title, url):

        self.proxy.new_har(title)
        self.driver.get(url)
        result = json.dumps(self.proxy.har, ensure_ascii=False)
        self.__store_into_file(title, result)

    def stop_all(self):
        """stop server and driver"""
        self.server.stop()
        self.driver.quit()



if __name__ == '__main__':
    # path_har = 'stackoverflow.har'
    # get_total_data_content(path_har)

    path = "browsermob-proxy-2.1.4/bin/browsermob-proxy.bat"
    RUN = CreateHar(path)
    RUN.start_all()
    RUN.create_har('youtube', 'https://www.youtube.com/watch?v=knW7-x7Y7RE')
    RUN.create_har('stackoverflow', 'http://stackoverflow.com')
    RUN.stop_all()
