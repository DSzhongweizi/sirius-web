#!/usr/bin/python
# -*- coding: UTF-8 -*-

from keras.models import load_model
import numpy as np

def data_in_one(array):
    threshold = np.load("model/threshold.npy")
    if array.ndim==1:#如果是一维数组
        for i in range(63):
            array[i] = (array[i]-min(threshold[0][i],array[i]))/(max(threshold[1][i],array[i])-min(threshold[0][i],array[i]))
            return array
    else:
        for i in range(array.shape[1]):#其他
            a=array[:,i]
            array[:,i] = (a-min(threshold[0][i],min(a)))/(max(threshold[1][i],max(a))-min(threshold[0][i],min(a)))
            return array

def pred(array):
    if array.shape[0]!=63:
        print("输入数据有误")
    array=data_in_one(array)
    model = load_model('model/Our_model.h5')
    result=model.predict(array.reshape(-1,63))
    return result.reshape((1,-1))