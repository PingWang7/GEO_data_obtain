# -*- coding: utf-8 -*-
# @Time     : 2021/9/26 9:46
# @Author   : Ping
# @File     : getSRRurl.py
# @Software : PyCharm

import os

import click
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent(path="fake_useragent_0.1.11.json")


class GetDownloadUrl:
    def __init__(self, srr_filePath):
        self.srr_filePath = srr_filePath
        self.srr_fileSavePath = "%s_downloadURLs.txt" % srr_filePath
        self.srr_srr_list = sorted(open(self.srr_filePath, 'r').read().strip().split('\n'))
        if os.path.exists(self.srr_fileSavePath):
            with open(self.srr_fileSavePath) as fr:
                self.srr_urlList = list(set([x.strip() for x in fr.readlines()]))
                self.haveGotSRR = [x.split("/")[-1].split(".")[0] for x in self.srr_urlList]
        else:
            self.srr_urlList = []
            self.haveGotSRR = []

    def write_out(self):
        with open(self.srr_fileSavePath, "w") as fw:
            fw.write("\n".join(self.srr_urlList))

    def __log(self):
        statistics = {"Sum SRR": len(self.srr_srr_list),
                      "Got URL": len(self.haveGotSRR),
                      "Not Get": len(self.srr_srr_list) - len(self.haveGotSRR)}
        print("Progress Log".center(18, " ").center(50, "#"))
        for key, value in statistics.items():
            print("%s" % ("%s: %3d" % (key, value)).center(50))
        print("#" * 50)

    def get_srr_url(self):
        proxies = {"http": None, "https": None}
        for sraID in self.srr_srr_list:
            web_url = 'https://trace.ncbi.nlm.nih.gov/Traces/sra/?run=%s' % sraID
            if sraID in self.haveGotSRR:
                continue
            print("【 %3d of %d %s 】" % (self.srr_srr_list.index(sraID) + 1, len(self.srr_srr_list), sraID), end="")
            try_time = 0
            condition = 0
            while condition == 0:
                try:
                    headers = {"User-Agent": ua.random,
                               'Connection': 'close'}
                    html = requests.get(web_url,
                                        stream=True,
                                        proxies=proxies,
                                        headers=headers,
                                        timeout=60).text
                    soup = BeautifulSoup(html, features="html.parser")

                    url_list = [x.text for x in
                                soup.find('table', class_='geo_zebra run-viewer-download').find_all('a')]
                    ncbi_url = [x for x in url_list if 'ncbi.nlm.nih' in x][0]
                    print(" downloadURL: %-100s" % ncbi_url, end="\r")
                    self.srr_urlList.append(ncbi_url)
                    self.haveGotSRR.append(sraID)
                    condition = 1
                    self.write_out()
                except Exception as e:
                    try_time += 1
                    print("\t\t[%d of 5] | %s | %s]" % (try_time, sraID, str(e)), end="\r")
                    if try_time > 2:
                        condition = 1

        print()
        self.__log()


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--srr_path', "-s", help='SRR data Path')
def start_task(srr_path):
    task = GetDownloadUrl(srr_path)
    task.get_srr_url()


if __name__ == "__main__":
    start_task()
