#!/usr/bin/python
from flask import Flask, render_template, request, redirect, send_from_directory
from flask_bootstrap import Bootstrap
from bs4 import BeautifulSoup
import time, sys, random
import requests

import search

app = Flask(__name__)
Bootstrap(app)

user_agents = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36", \
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
      'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
     'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
     (KHTML, like Gecko) Element Browser 5.0', \
     'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
     'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
     'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
     'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
     Version/6.0 Mobile/10A5355d Safari/8536.25', \
     'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
     Chrome/28.0.1468.0 Safari/537.36', \
     'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)'
    ]

@app.route('/')
@app.route('/home')
def index():
    keyword = request.args.get('keyword')
    page = request.args.get('page')
    cat = request.args.get('cat')

    if type(page) != type(None):
        print "page: " + str(page)
    else:
        page = "1"

    if type(keyword) != type(None):
        print "keyword: " + str(keyword)

        if int(page) < 1:
            return render_template('index.html', \
                        dangerAlert="Error: Invalid Page Number", \
                        keyword=None)

        items = search.getItems(keyword, page, int(cat))
        return render_template('index.html', \
                dangerAlert="", \
                curTime=str(time.asctime()), \
                curPage=str(page), \
                keyword=keyword, \
                cat=cat, \
                items=items)
    return render_template('index.html', keyword=None, items=None)

@app.route('/lucky/<keyword>')
def googleLucky(keyword):
    luckyUrl = "http://www.google.com/webhp?#q=" + keyword + "&btnI=I"
    r = requests.get(luckyUrl)
    redirectUrl = r.url
    print "[lucky] Redirect to " + redirectUrl

    searchUrl="https://www.google.com.hk/search?hl=en&q=" + keyword
    r = requests.get(searchUrl, headers={\
        'User-agent': user_agents[random.randint(0, len(user_agents))]\
        })
    soup = BeautifulSoup(r.content.decode('utf-8','ignore') )
    print r.content
    sys.stdout.flush()
    tags = soup.select("h3 a")
    if len(tags) > 0:
        tag = str(tags[0])
        print "tag: " + tag
        if tag.find("url=http") != -1:
            start = tag.find("url=http") + len("url=")
        elif tag.find("url?q=http") != -1:
            start = tag.find("url?q=http") + len("url?q=")
        else:
            start = tag.find('href="') + len('href="')
        end = start
        while tag[end] != '"':
            end += 1
        firstResultUrl = tag[start:end].replace('%3A', ':').replace('%2F', '/')
        return redirect(firstResultUrl)
    else:
        return redirect(luckyUrl)

@app.route('/google/<keyword>')
def google(keyword):
    searchUrl="https://www.google.com.hk/search?hl=en&q=" + keyword
    r = requests.get(searchUrl, headers={\
        'User-agent': user_agents[random.randint(0, len(user_agents))]\
        })
    return r.content

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
