# -*- coding: utf-8 -*-
# @Time       : 2022/3/3 14:26
# @Author     : Ping
# @File       : search_geoData.py
# @Software   : PyCharm

import os
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


# cmd = '''"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222'''
# os.system(cmd)

class Browser:
    def __init__(self, webdriver_path='模拟浏览器/chromedrivers/chromedriver_win32_98/chromedriver.exe'):
        self.webdriver_path = webdriver_path
        self.browser = None

    def open_browser(self):
        options = webdriver.ChromeOptions()
        s = Service(self.webdriver_path)
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument("--disable-blink-features=AutomationControlled")
        useragent = UserAgent(path="fake_useragent.json").random
        options.add_argument(f'user-agent={useragent}')
        options.add_argument('--lang=zh-cn')  # 此句是为了让网页以中文的形式显示
        # options.add_experimental_option("debuggerAddress", "localhost:9222")
        self.browser = webdriver.Chrome(service=s,
                                        options=options)
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
              get: () => undefined
            })
          """
        })

    def geo_search(self, term):
        """

        Args:
            term: search term, example: '(((Melanoma) AND rna seq[Description])) AND Homo sapiens[Organism]'

        Returns:

        """
        self.browser.get('https://www.ncbi.nlm.nih.gov/gds/')
        search_input = self.browser.find_element('xpath', '//*[@id="term"]')
        search_input.clear()
        search_input.send_keys(term)
        search_input.submit()
        selector = self.browser.find_element('xpath', '//*[@id="maincontent"]/div/div[1]/ul/li[2]')
        selector.click()
        while True:
            try:
                selector_s1 = self.browser.find_element('xpath',
                                                           '//*[@id="ps500"]')
                selector_s1.click()
                break
            except:
                pass

        # 筛选series
        selector = browser.browser.find_element('xpath', '//*[@id="_entryTypeGds"]/li/ul/li[2]/a')
        selector.click()


browser = Browser()

browser.open_browser()

browser.geo_search('(((Melanoma) AND rna seq[Description])) AND Homo sapiens[Organism]')

html = browser.browser.page_source

soup = BeautifulSoup(html, features="html.parser")

items = soup.find_all('div', class_='rprt')


infos = []

for i in range(len(items)):
    print(i+1)
    it = items[i]
    title = it.a.text
    url = "https://www.ncbi.nlm.nih.gov/%s" % it.a["href"]
    description = it.select('div.supp')[0].text.split(" more...")[0]
    
    organism, types = [x.text.split(': ')[1] for x in it.select('dl.details')[:2]]
    
    platform, sample_num = it.select('dl.details')[2].dd.text, \
                           it.select('dl.details')[2].dd.next_sibling.text
    
    accession = [x.strip() for x in it.select('div.resc')[0].find_all(text=True)
                 if x.strip().startswith("GSE")][0]
    notes = it.select('p.links.nohighlight')[0].text
    infos.append([accession, sample_num, title, url, description, organism, types, platform, notes])

output = pd.DataFrame(infos)

output.to_csv("info.txt", sep="\t", index=False)


browser.browser.get(url)

html = browser.browser.page_source

soup = BeautifulSoup(html, features="html.parser")

[x.text for x in soup.find_all('tr', valign="top")]





