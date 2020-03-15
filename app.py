#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask,request
from flask_cors import CORS
import os,csv
app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/apis/uploadFile',methods=['POST'])
def uploadFile():
    filelist={}
    file=request.files['file']
    path=os.path.join('static/', file.filename)
    file.save(path)
    if file:
        k=0
        with open(path) as file:
            for row in csv.reader(file):
                # filelist.append(row);
                filelist[k]=row
                k=k+1
    return filelist


if __name__ == '__main__':
    app.run()
