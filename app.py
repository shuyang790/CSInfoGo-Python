#!/usr/bin/python
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

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
                totalPage=pageInfo["totalPage"], \
                curPage=pageInfo["curPage"], \
                prevPage=str(int(pageInfo["curPage"]) - 1) if \
                    pageInfo["curPage"] != "1" else "1", \
                nextPage=str(int(pageInfo["curPage"]) + 1) if \
                    pageInfo["curPage"] != pageInfo["totalPage"] \
                    else pageInfo['totalPage'], \
                keyword=keyword, \
                items=items)
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='::', debug=True, port=4000)
