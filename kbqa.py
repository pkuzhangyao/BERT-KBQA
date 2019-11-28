from terminal_predict import predict_service
from Data.load_dbdata import upload_data
from datetime import time, timedelta, datetime
from kbqa_test import estimate_answer
import pandas as pd
from run_similarity import BertSim
import tensorflow as tf
from global_config import Logger

loginfo = Logger("recommend_articles.log", "info")
bs = BertSim()
bs.set_mode(tf.estimator.ModeKeys.PREDICT)

while True:
    choice = {}
    question = input("question:")
    start1 = datetime.now()
    ner = predict_service(question)
    print("识别出的实体:{}".format(ner))
    sql_e1 = "select * from nlpccQA where entity ='" + ner + "' order by length(entity) asc "
    result_e1 = list(upload_data(sql_e1))
    print("从数据库中精确找到实体{}个".format(len(result_e1)))
    result = result_e1
    if len(result_e1) == 0:
        print("精确查找没有查找到实体，采用模糊查找")
        sql_e0 = "select * from nlpccQA where entity like '%" + ner + "%' order by length(entity) asc "
        result_e0 = list(upload_data(sql_e0))
        print(result_e0)
        if len(result_e0) == 0:
            print("这个问题我也不知道呀~~")
            continue
        k = 1
        entity_candidate = [result_e0[0][0], 0]
        # [实体，start, end]
        flag = 0
        for i in range(1, len(result_e0)):
            if result_e0[i][0] != result_e0[i - 1][0]:
                entity_candidate.append(i - 1)
                choice[k] = entity_candidate
                k += 1
                entity_candidate = [result_e0[i][0], i]
                flag = 1
            else:
                continue
        if flag == 0:  # 只有一个实体的情况
            entity_candidate.append(len(result_e0)-1)
            choice[k] = entity_candidate
        print(choice)
        print("您要问的是下列哪一个呢？")
        for key in choice.keys():
            print(key, choice[key][0])
        print(len(choice)+1, "以上都不是")
        your_choice = input("请输入要选择的序号：")
        if int(your_choice) == len(choice)+1:
            print("这个问题我也不知道呀~~")
            continue
        start = choice[int(your_choice)][1]
        end = choice[int(your_choice)][2]
        for i in range(start, end + 1):
            result.append(result_e0[i])

    #print(result_e0_a1)
    print('数据库中查找实体用时: {} sec'.format((datetime.now() - start1).seconds))
    if len(result) > 0:
        answer = False
        # 非语义匹配，加快速度
        # l1[0]: entity
        # l1[1]: attribute
        # l1[2]: answer
        flag_ambiguity = True
        start = datetime.now()
        for l in result:  # l是从数据库中查出来的所有符合实体的三元组
            if l[1] in question or l[1].lower() in question or l[1].upper() in question:
                print("在知识库中查找到完全匹配的三元组:{}，用时：{} sec".format(l, (datetime.now() - start).seconds))
                answer = True
                print("问题:'{}'的答案是：'{}'".format(question, l[2]))
                print("总用时为:{} sec".format((datetime.now() - start1).seconds))
                break
            #time.sleep(1)
            continue
        if answer:
            continue
        # 语义匹配
        result_df = pd.DataFrame(result, columns=['entity', 'attribute', 'value'])
        # loginfo.logger.info(result_df.head(100))
        print("开始相似度计算")
        start = datetime.now()
        attribute_candicate_sim = [(k, bs.predict(question, k)[0][1]) for k in result_df['attribute'].tolist()]
        print("相似度计算耗时:{} sec".format((datetime.now() - start).seconds))
        attribute_candicate_sort = sorted(attribute_candicate_sim, key=lambda candicate: candicate[1], reverse=True)
        print(attribute_candicate_sort)
        #loginfo.logger.info("\n".join([str(k) + " " + str(v) for (k, v) in attribute_candicate_sort]))
        """
        2019-09-20 10:41:47,080|kbqa.py[line:51]|<module>|INFO|身高 0.99359435
        登录身高 0.9573191
        体重 0.60461545
        单节最高分 0.14882813
        单场最高得分 0.034205496
        登录体重 0.00237097
        """
        answer_candicate_df = result_df[result_df["attribute"] == attribute_candicate_sort[0][0]]
        if float(attribute_candicate_sort[0][1])<0.8:
            print("计算出最高相似度为 {}".format(attribute_candicate_sort[0]))
            print("这道题超出我的能力啦~~")
            continue
        print(answer_candicate_df)
        print("问题:'{}'的答案是：'{}'".format(question, answer_candicate_df["value"].values[0]))
        print("总用时为:{} sec".format((datetime.now() - start1).seconds))
    #time.sleep(1)