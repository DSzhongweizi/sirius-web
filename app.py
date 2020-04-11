#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask import Flask,request,render_template,url_for
from flask_cors import CORS
from process_data import process_file
import os,csv
app = Flask(__name__, static_folder='', static_url_path='')
CORS(app, supports_credentials=True)

@app.route('/apis/uploadFile',methods=['POST'])
def uploadFile():
    filelist={}
    file=request.files['file']
    path=os.path.join('static/file/uploaded-file/', file.filename)
    file.save(path)
    if file:
        k=0
        with open(path) as file:
            for row in csv.reader(file):
                filelist[k]=row
                k=k+1
    return filelist
@app.route('/apis/deleteFile',methods=['GET'])
def deleteFile():
    return process_file.delete_file(request.args.get('filename'))
@app.route('/apis/submitForm',methods=['POST'])
def submitForm():
    if request.form['is_upload'] == "true" :
        process_file.add_file()
        process_file.merge_file()
        result = process_file.read_file()
    else:
        result = process_file.not_file(request.form.to_dict())
    print(result)
    return render_template("result.html",result=result)

if __name__ == '__main__':
    app.run()
