#!/usr/bin/python
# -*- coding: UTF-8 -*-

import csv,os
import pandas as pd
import numpy as np
from process_data import model

UPLOADED_FILE_PATH = 'static/file/uploaded-file/'
PROCESSED_FILE_PATH = 'static/file/processed-file/'

def not_file(input_dict):
    input_dict.pop('year_select')
    input_list = list(map(float, list(input_dict.values())[0:-2]))
    if float(input_dict['retained_profits_1'])<=0 and float(input_dict['retained_profits_2'])<0 and float(input_dict['retained_profits_3'])<0:
        input_list.insert(1,1)
    else: input_list.insert(1,0)
    if float(input_dict['total_assets_1']) != 0 and \
        float(input_dict['total_assets_2']) != 0 and \
        float(input_dict['total_assets_3']) != 0:
        if (float(input_dict['total_liabilities_1'])/float(input_dict['total_assets_1'])>0.5 and
            float(input_dict['total_liabilities_2'])/float(input_dict['total_assets_2'])>0.5 and
            float(input_dict['total_liabilities_2']) > float(input_dict['total_liabilities_1'])) or\
            (float(input_dict['total_liabilities_2'])/float(input_dict['total_assets_2'])>0.5 and
            float(input_dict['total_liabilities_3'])/float(input_dict['total_assets_3'])>0.5 and
            float(input_dict['total_liabilities_3']) > float(input_dict['total_liabilities_2'])):
            input_list.insert(2, 1)
        else: input_list.insert(2,0)
    else:input_list.insert(2,0)
    return np.vstack(([1], model.pred(np.array(input_list)))).T.astype(np.int32)
def delete_file(filename):
    os.remove(UPLOADED_FILE_PATH+filename)
    return '200'
def add_file():
    ID = []
    train_len = 0
    with open(UPLOADED_FILE_PATH+"base.csv", "r", encoding='gbk') as csvfile:
        read = csv.reader(csvfile)
        for row in read:
            if row[0] == 'ID':
                continue
            train_len += 1
            ID.append(row[0])
    report_ID = []
    profit = []
    result1 = []
    result2 = []
    Assert = []
    Debet = []
    with open(UPLOADED_FILE_PATH+"report.csv", "r", encoding='gbk') as csvfile:
        read = csv.reader(csvfile)
        for row in read:
            if row[0] == 'ID':
                continue
            report_ID.append(row[0])
            Assert.append(row[3])
            Debet.append(row[4])
            profit.append(row[8])

    for id in ID:
        flag = 0
        record1 = 0
        record2 = 0
        for n in range(report_ID.count(id)):
            sec = flag
            flag = report_ID[flag:].index(id)
            index = flag + sec
            if report_ID[index] == id and float(profit[index]) <= 0:
                record1 += 1
            if n != 0 and float(Debet[sec - 1]) / float(Assert[sec - 1]) > 0.5 and float(Debet[index]) > float(
                    Debet[sec - 1]):
                record2 += 1
            flag = index + 1
        if record1 >= 3:
            result1.append(1)
        else:
            result1.append(0)
        if record2 >= 2:
            result2.append(1)
        else:
            result2.append(0)
    # hstack将具有相同的数据结构的列表和元组组合成numpy数组
    # mat将字符串以分号(；)分割，或者为列表形式以逗号（，）分割的数据生成矩阵
    # tolist将数组或者矩阵转换成列表
    l = np.hstack(((np.mat(ID).T).tolist(), (np.mat(result1).T).tolist(), (np.mat(result2).T).tolist()))
    l1 = l[0:train_len]
    l2 = l[train_len:]
    # 将新增的文件也当作上传文件合并到一个文件夹中
    with open(PROCESSED_FILE_PATH+"add.csv", "w", newline='', encoding='gbk') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', '是否连续亏损三年及以上', '连续两年满足T-1年资产负债率超过50%，第t年负债增长'])
        for row in l1:
            writer.writerow(row)
def merge_file():
    add = pd.read_csv(PROCESSED_FILE_PATH + "add.csv", encoding="gbk")
    base = pd.read_csv(UPLOADED_FILE_PATH + "base.csv", encoding="gbk")
    knowledge = pd.read_csv(UPLOADED_FILE_PATH + "knowledge.csv", encoding="gbk")
    money = pd.read_csv(UPLOADED_FILE_PATH + "money.csv", encoding="gbk")
    year = pd.read_csv(UPLOADED_FILE_PATH + "report.csv", encoding="gbk")
    # axis=0纵向合并 axis=1横向合并
    add_base_knowledge = pd.concat([add,base,knowledge], axis=1)
    add_base_knowledge.to_csv(PROCESSED_FILE_PATH + 'add_base_knowledge.csv', index=False,encoding="utf_8_sig")
    # --------------3.7-------------把三年的放在放在一行-train
    money.sort_values(by=['ID', 'year'], inplace=True)
    money.reset_index(inplace=True, drop=True)# 删除索引，后面的cancat连接就是根据索引来的
    year.sort_values(by=['ID', 'year'], inplace=True)
    year.reset_index(inplace=True, drop=True)
    money_report_tmp = pd.concat([money,year], axis=1)
    i = 0
    k = 0
    newhead = list(money_report_tmp.columns.values)[0:] + list(money_report_tmp.columns.values)[0:] + list(money_report_tmp.columns.values)[0:]
    money_report = pd.DataFrame(columns=newhead)
    # money_report['ID'].notnull
    while i<=3:
        newrow = list(money_report_tmp.loc[i].values) + list(money_report_tmp.loc[i + 1].values)+ list(money_report_tmp.loc[i + 2].values)
        i += 3
        money_report.loc[k] = newrow
        k += 1
    money_report.to_csv(PROCESSED_FILE_PATH + 'money_report.csv', index=False, encoding="utf_8_sig")
    merge = pd.concat([add_base_knowledge, money_report], axis=1)
    merge.to_csv(PROCESSED_FILE_PATH + 'merged_file.csv', index=False, encoding="utf_8_sig")
def read_file():
    merge=pd.read_csv(PROCESSED_FILE_PATH + "merged_file.csv",encoding="utf_8_sig")
    id=np.array(merge['ID'].tolist())
    drop_columns=[]
    for col in merge.columns.values.tolist():
        if 'ID' in col or 'flag' in col or 'year' in col:
            drop_columns.append(col)
    merge.drop(drop_columns,axis=1,inplace=True)
    # 转化成数组
    merge = merge.values.reshape((63,-1))
    return np.vstack((id, model.pred(merge))).T.astype(np.int32)