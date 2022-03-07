# -*- coding: utf-8 -*-
# @Time     : 2022/2/11 22:36
# @Author   : Ping
# @File     : get_AccessionList.py
# @Software : PyCharm

import os
import random
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# cmd = '''"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222'''
# os.system(cmd)

tissue = "melanoma"

options = webdriver.ChromeOptions()
out_path = 'E:\\工作\\2022-01-10-1 01_癌症微生物数据库\\癌症微生物数据库\\GEO accession list\\%s' % tissue + '\\'  # 是你想指定的路径

if not os.path.exists(out_path):
    os.mkdir(out_path)
prefs = {'profile.default_content_settings.popups': False,  # 取消弹窗
         'download.default_directory': out_path,  # 下载保存路径
         "profile.default_content_setting_values.automatic_downloads": 1  # 允许多文件下载
         }
options.add_experimental_option('useAutomationExtension', False)
options.add_experimental_option('excludeSwitches', ['enable-automation'])
options.add_argument("--disable-blink-features=AutomationControlled")
userAgent = UserAgent(path="fake_useragent.json").random
options.add_argument(f'user-agent={userAgent}')
options.add_experimental_option('prefs', prefs)
options.add_argument('--lang=zh-cn')  # 此句是为了让网页以中文的形式显示
# options.add_experimental_option("debuggerAddress", "localhost:9222")
browser = webdriver.Chrome(executable_path=r"模拟浏览器/chromedrivers/chromedriver_win32_98/chromedriver.exe",
                           options=options)
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    })
  """
})


def rename_dl_file(save_path, project_id):
    while True:
        file_list = os.listdir(save_path)
        if "SRR_Acc_List.txt" in file_list:
            os.rename("%s\\SRR_Acc_List.txt" % save_path,
                      "%s\\Accession_list\\%s_SRR_Acc_List.txt" % (save_path, project_id))
            print("Save data: %s_SRR_Acc_List.txt" % project_id)
            return 0
        if "SraRunTable.txt" in file_list:
            os.rename("%s\\SraRunTable.txt" % save_path,
                      "%s\\metaData\\%s_SraRunTable.csv" % (save_path, project_id))
            print("Save data: %s_SraRunTable.txt" % project_id)
            return 0
        time.sleep(0.001)


df = pd.read_excel(r"E:\工作\2022-01-10-1 01_癌症微生物数据库\癌症微生物数据库\GEO_RNAseq.xlsx",
                   sheet_name=tissue)

project_list = df[df.columns[0]].tolist()

unGotList = []
for project in project_list:
    print("%s %d of %d" % (project, project_list.index(project) + 1, len(project_list)))
    url = "https://www.ncbi.nlm.nih.gov/Traces/study/?acc=%s" % project + "&o=acc_s%3Aa"
    browser.get(url)
    if not os.path.exists("%sAccession_list" % out_path):
        os.mkdir("%sAccession_list" % out_path)
    if not os.path.exists("%smetaData" % out_path):
        os.mkdir("%smetaData" % out_path)
    html = browser.page_source
    while ('t-acclist-all' not in html) & ("Nothing has been found for accession" not in html):
        html = browser.page_source
        time.sleep(0.01)
    if "Nothing has been found for accession" in html:
        unGotList.append(project)
        continue
    # 下载 accession list
    if not os.path.exists("%s\\Accession_list\\%s_SRR_Acc_List.txt" % (out_path, project)):
        bottom1 = browser.find_element("xpath", '//*[@id="t-acclist-all"]')
        bottom1.click()
        rename_dl_file(out_path, project)
        time.sleep(0.01)
    if not os.path.exists("%s\\metaData\\%s_SraRunTable.csv" % (out_path, project)):
        bottom2 = browser.find_element('xpath', '//*[@id="t-rit-all"]')
        bottom2.click()
        rename_dl_file(out_path, project)
        time.sleep(0.01)

print("\nunGotList:\n%s" % "\n".join(unGotList))
