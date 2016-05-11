#!/usr/bin/python
from flask import Flask, render_template, request, redirect, send_from_directory
from flask_bootstrap import Bootstrap
from bs4 import BeautifulSoup
import time, sys
import requests

import search

app = Flask(__name__)
Bootstrap(app)

@app.route('/')
@app.route('/home')
def index():
    keyword = request.args.get('keyword')
    page = request.args.get('page')

    if type(page) != type(None):
        print "page: " + str(page)
    else:
        page = "1"

    if type(keyword) != type(None):
        print "keyword: " + str(keyword)

        pageInfo, items = search.getItems(keyword, page)
        return render_template('index.html', \
                curTime=str(time.asctime()), \
                totalPage=pageInfo["totalPage"], \
                curPage=pageInfo["curPage"], \
                prevPage=str(int(pageInfo["curPage"]) - 1) if \
                    pageInfo["curPage"] != "1" else "1", \
                nextPage=str(int(pageInfo["curPage"]) + 1) if \
                    pageInfo["curPage"] != pageInfo["totalPage"] \
                    else pageInfo['totalPage'], \
                keyword=keyword, \
                items=items)
    return render_template('index.html', keyword=None)

@app.route('/lucky/<keyword>')
def googleLucky(keyword):
    luckyUrl = "http://www.google.com/webhp?#q=" + keyword + "&btnI=I"
    r = requests.get(luckyUrl)
    redirectUrl = r.url
    print "[lucky] Redirect to " + redirectUrl

    searchUrl="https://www.google.com.hk/search?hl=en&q=" + keyword
    r = requests.get(searchUrl, headers={'User-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36"})
    soup = BeautifulSoup(r.content.decode('utf-8','ignore') )
    print r.content
    sys.stdout.flush()
    tags = soup.select("h3 a")
    if len(tags) > 0:
        tag = str(tags[0])
        print "tag: " + tag
        start = tag.find("url=http") + len("url=")
        end = start
        while tag[end] != '"':
            end += 1
        firstResultUrl = tag[start:end].replace('%3A', ':').replace('%2F', '/')
    return redirect(redirectUrl)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/img/<filename>')
def img(filename):
    return send_from_directory('img', filename)

@app.route('/css/<filename>')
def css(filename):
    return send_from_directory('css', filename)

@app.route('/js/<filename>')
def js(filename):
    return send_from_directory('js', filename)

if __name__ == '__main__':
    app.run(host='::', debug=True, port=4000)
