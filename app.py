from flask import Flask, render_template, request
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import requests
import urllib
import json
import re
from PIL import Image
from io import BytesIO
from numpy import zeros
# -*- coding: utf-8 -*-
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route('/', methods = ['GET'])
def index():
    file = os.listdir('static/popular')
    musicAll = []
    textAll = []
    imgAll = []
    for i in file:
        if os.path.splitext(i)[1] ==".txt":
            textAll.append(i)
        elif os.path.splitext(i)[1] ==".mp3":
            musicAll.append(i)
        elif os.path.splitext(i)[1] ==".png":
            imgAll.append(i)
    music = []
    text = []
    img = []
    for i in range(0, 60):
        music.append(musicAll[i])
        text.append(textAll[i])
        img.append(imgAll[i])

    textInfo = [[]]
    for i in range(0, 60):
        textInfo.append([])
        f = open(r"static/popular/" + text[i])
        all_lines = f.readlines()
        cnt = 0
        for line in all_lines:
            textInfo[i].append(line.decode('GB2312'))
            cnt=cnt+1
            if(cnt == 3):
                break

        music[i] = "static/popular/" + music[i]
        img[i] = "static/popular/" + img[i]

    lenstr = len(img[0])
    return render_template('PopularPage.html', textInfo = textInfo, music = music, img = img, lenstr = lenstr)

@app.route('/soso', methods = ['GET'])
def soso():
    file = os.listdir('static/soso')
    musicAll = []
    textAll = []
    imgAll = []
    for i in file:
        if os.path.splitext(i)[1] ==".txt":
            textAll.append(i)
        elif os.path.splitext(i)[1] ==".mp3":
            musicAll.append(i)
        elif os.path.splitext(i)[1] ==".png":
            imgAll.append(i)
    music = []
    text = []
    img = []
    for i in range(0, 48):
        music.append(musicAll[i])
        text.append(textAll[i])
        img.append(imgAll[i])
    textInfo = [[]]
    for i in range(0, 48):
        textInfo.append([])
        f = open(r"static/soso/" + text[i])
        all_lines = f.readlines()
        cnt = 0
        for line in all_lines:
            textInfo[i].append(line.decode('GB2312'))
            cnt=cnt+1
            if(cnt == 3):
                break

        music[i] = "static/soso/" + music[i]
        img[i] = "static/soso/" + img[i]
    return render_template('SosoPage.html', textInfo = textInfo, music = music, img = img)

class SearchSong(FlaskForm):
    searchsong = StringField('Search', validators=[DataRequired(), Length(min=0, max=20)])
    submit = SubmitField('Search')

@app.route('/search', methods = ['GET', 'POST'])
def search():
    num = 0
    errorNum = 0
    if(request.method == 'POST'):
        name = request.form['search']
        if name == "":
            form = SearchSong()
            return render_template('Search.html', title='Search', form=form)
        print(name)
        res1 = requests.get(
            'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?&t=0&aggr=1&cr=1&catZhida=1&lossless=0&flag_qc=0&p=1&n=20&w=' + name)
        jm1 = json.loads(res1.text.strip('callback()[]'))
        jm1 = jm1['data']['song']['list']

        mid = []
        songmid=[]
        songname=[]
        singer=[]
        res2=[]
        jm2=[]
        vkey=[]
        flag=zeros(12)
        if len(jm1) > 12:
            num = 12
        else:
            num = len(jm1)
        for i in range(0, num):
            for j in range (0, i):
                if songname[j-errorNum] == jm1[i]['songname']:
                    flag[j]+=1
                    jm1[i]['songname']+=str(flag[j])
                    print("jm1[i]['songname']" + jm1[i]['songname'])
            try:
                print(i)
                mid.append(jm1[i]['media_mid'])
                songmid.append(jm1[i]['songmid'])
                songname.append(jm1[i]['songname'])
                singer.append(jm1[0]['singer'][0]['name'])
                res2.append(requests.get(
                    'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?&jsonpCallback=MusicJsonCallback&cid=205361747&songmid=' +
                    songmid[i-errorNum] + '&filename=C400' + mid[i-errorNum] + '.m4a&guid=6612300644'))
                jm2.append(json.loads(res2[i-errorNum].text))
                vkey.append(jm2[i]['data']['items'][0]['vkey'])
                src = 'http://dl.stream.qqmusic.qq.com/C400' + mid[i-errorNum] + '.m4a?vkey=' + vkey[
                    i-errorNum] + '&guid=6612300644&uin=0&fromtag=66'
                print('For ' + songname[i-errorNum] + ' Start download...')
                print(songname[i-errorNum] + ' - ' + singer[i-errorNum] + '.mp3 ' + ' Downloading...')
                try:
                    urllib.urlretrieve(src, 'static/scrape/' + songname[i-errorNum] + '.mp3')
                except:
                    print('Download wrong')
                print('[' + songname[i-errorNum] + '] Download complete')
                # images
                src = 'http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word='
                url = src + songname[i-errorNum] + singer[i-errorNum]
                result = requests.get(url)
                addrs = re.findall('"objURL":"(.*?)"', result.text, re.S)
                addr = addrs[0]
                pic = requests.get(addr, timeout=10)
                img = Image.open(BytesIO(pic.content))
                new_img = img.resize((140, 140))
                new_img.save('static/scrape/' + songname[i-errorNum] + '.png')
            except:
                print('Get wrong')
                print(i)
                errorNum=errorNum+1
                continue
        textInfo=[[]]
        music=[]
        img = []
        for i in range(0, num-errorNum):
            textInfo.append([])
            textInfo[i].append(songname[i])
            textInfo[i].append(singer[i])
            textInfo[i].append("5")
            musicSrc = "static/scrape/" + songname[i] + ".mp3"
            imgSrc = "static/scrape/" + songname[i] + ".png"
            music.append(musicSrc)
            img.append(imgSrc)
        lenstr = len(img[0])
        return render_template('reptile.html', textInfo = textInfo, music = music, img = img, lenstr = lenstr, num = num-errorNum)
    form = SearchSong()
    return render_template('Search.html', title = 'Search', form = form)

@app.route('/artist', methods = ['GET'])
def artist():
    return render_template('Artists.html')

@app.route('/contact', methods = ['GET'])
def contact():
    return render_template('ContactUs.html')

if(__name__ == "__main__"):
    app.run(port = 5000, debug=True)
