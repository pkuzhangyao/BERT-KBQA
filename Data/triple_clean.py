# -*- coding: utf-8 -*-
# @Time    : 2019/4/18 20:16
# @Author  : Alan
# @Email   : xiezhengwen2013@163.com
# @File    : triple_clean.py
# @Software: PyCharm


import pandas as pd


'''
构造数据库
'''

triple_list = []
seq_q_list = []    #["中","华","人","民"]
seq_tag_list = []  #[0,0,1,1]

file = "C:/Users/zhang/Desktop/nlpcc-iccpol-2016.kbqa.kb"
#file = "./NLPCC2016KBQA/nlpcc-iccpol-2016.kbqa.kb"
i = 0
with open(file, 'r',encoding='utf-8') as f:
    for line in f:
        clean_triple = line.replace(" ","").strip().split("|||")
        if len(clean_triple) > 3:
            continue
        triple_list.append(clean_triple)
        i += 1
        if i % 10000000 == 0:
            if i == 10000000:
                df = pd.DataFrame(triple_list, columns=["entity", "attribute", "answer"])
                print(df)
                print(df.info())
                df.to_csv("./DB_Data/clean_triple.csv", mode='a', encoding='utf-8', index=False)
                print("已写入{}行数据".format(i))
                triple_list = []
            else:
                df = pd.DataFrame(triple_list, columns=["entity", "attribute", "answer"])
                #print(df)
                #print(df.info())
                df.to_csv("./DB_Data/clean_triple.csv", mode='a', encoding='utf-8', index=False, header=False)
                print("已写入{}行数据".format(i))
                triple_list = []

    df = pd.DataFrame(triple_list, columns=["entity", "attribute", "answer"])
    print(df)
    print(df.info())
    df.to_csv("./DB_Data/clean_triple.csv", mode='a', encoding='utf-8', index=False, header=False)
    #df.to_csv("./DB_Data/clean_triple1.csv", mode='a', encoding='utf-8', index=False, header=False)
    print("已写入{}行数据".format(i))
    triple_list = []

