# -*- coding: utf-8 -*-
# @Time     : 2022/2/12 10:19
# @Author   : Ping
# @File     : rename_flies.py
# @Software : PyCharm

import os

tissue = "kidney"

path = 'C:\\Users\\Administrator\\Desktop\\%s' % tissue + '\\'  # 是你想指定的路径
file_list = [x for x in os.listdir(path) if "SraRunTable" in x]

if not os.path.exists("%smetaData" % path):
    os.mkdir("%smetaData" % path)

for file in file_list:
    os.rename("%s\\%s" % (path, file),
              "%s\\metaData\\%s" % (path, file))


file_list = [x for x in os.listdir(path) if "SRR_Acc_List" in x]

if not os.path.exists("%sAccession_list" % path):
    os.mkdir("%sAccession_list" % path)

for file in file_list:
    os.rename("%s\\%s" % (path, file),
              "%s\\Accession_list\\%s" % (path, file))







