#!/usr/bin/env python

import sys
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import time

def article_to_item(article):
    item = ET.Element('item')
    title = ET.SubElement(item, 'title')
    title.text = article.h1.text.strip()
    enclosure = ET.SubElement(item, 'enclosure')
    enclosure.set('url', article.select(".dl_track")[0]['href'].strip())
    enclosure.set('type', 'audio/mpeg')
    url = requests.head(article.select(".dl_track")[0]['href'].strip()).headers['location']
    url2 = requests.head(url).headers['location']
    enclosure.set('length', requests.head(url2).headers['content-length'])
    guid = ET.SubElement(item, 'guid')
    guid.text = "99pi:" + article.h1.text.strip()
    return item


orig_feed = requests.get('http://feeds.99percentinvisible.org/99percentinvisible?format=xml')
feed = ET.fromstring(orig_feed.text)
chan = feed.find('channel')
for elem in chan.findall('item'):
    chan.remove(elem)

i = 18
while (True):
    try:
        page = requests.get('http://99percentinvisible.org/category/episode/page/' + str(i))
        if (page.status_code == 404):
            break

        soup = BeautifulSoup(page.text)
        articles = soup.find(id='centercol').find_all('article') 
        items = map(article_to_item, articles)
        for item in items:
            chan.append(item)

        time.sleep(2)
        i += 1
    except requests.exceptions.ConnectionError:
        time.sleep(4)

ET.dump(feed)
