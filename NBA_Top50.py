import requests
from bs4 import BeautifulSoup
import pymongo
from requests_study.NBA_top50.config import *
import re

client = pymongo.MongoClient('localhost', 27017)
db = client[MONGO_DB]

class NbaTop:

    def __init__(self, base_url, seeLz):
        self.base_url = base_url
        self.seeLz = '?see_lz=' + str(seeLz)

    def get_soup(self, pageNum):
        headers = {'User_Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2595.400 QQBrowser/9.6.10872.400'}
        try:
            url = self.base_url + self.seeLz + '&pn=%s' % pageNum
            # print(url)
            response = requests.get(url, headers=headers).content
            soup = BeautifulSoup(response, 'lxml')
            return soup
        except Exception as e:
            print(e)

    def parse_title(self, soup):
        title = soup.select_one('div.left_section > div.clearfix > h3').get_text()
        return title

    def parse_info(self, soup):
        divs = soup.select('cc > div.d_post_content.j_d_post_content ')
        divs.pop(0)
        infos = []
        for div in divs:
            if div.select('img'):
                info = {}
                img_url = div.select_one('img')['src']
                desc = div.get_text()
                info['img_url'] = img_url
                info['desc'] = desc
                infos.append(info)
        return infos

    def save_to_mongodb(self, infos):
        db[MONGO_TABLE].insert(infos)

    def download_image(self, infos):
        pattern = re.compile(r'.*?.jpg')
        for info in infos:
            img_url = info['img_url']
            if re.search(pattern, img_url):
                filename = img_url[-44:]
                req = requests.get(img_url, stream=True)
                with open(r'./images/%s' % filename, 'wb') as f:
                    for chunk in req.iter_content(chunk_size=128):
                        f.write(chunk)

base_url = 'https://tieba.baidu.com/p/3138733512'
nbatop = NbaTop(base_url, 1)

soup = nbatop.get_soup(1)
title = nbatop.parse_title(soup)
print(title)

for pageNum in range(1,6):
    soup = nbatop.get_soup(pageNum)
    infos = nbatop.parse_info(soup)
    nbatop.save_to_mongodb(infos)
    nbatop.download_image(infos)

print('Programming Finshed')

