#*-encoding: utf-8 -*

import initDB

import os
import sqlite3

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

allItems = []
pageLen = 10

univName2Abbr = {}
univAbbr2Name = {}

def itemPerson(person, c):
    item = dict(zip(["Name", "UniversityAbbr", "URL", "ResearchInterests",\
            "ACMFellow", "IEEEFellow", "Funding"], list(person)))
    univ = c.execute("SELECT * FROM universities WHERE Abbr='" + item["UniversityAbbr"] + "'")\
        .fetchall()[0]
    item.update({ \
        "isPerson": "True", \
        "University": univ[0], \
        "CSRank": univ[3], \
        "AIRank": univ[4], \
        "PLRank": univ[5], \
        "SystemRank": univ[6], \
        "TheoryRank": univ[7], \
         })
    return item

def getItems(keyword, page):

    if not os.path.isfile("./data/csinfo.db"):
        initDB.main()

    global conn
    conn = sqlite3.connect("./data/csinfo.db")

    results = []
    keyword = keyword.strip()

    c = conn.cursor()

    c.execute("SELECT * FROM persons WHERE name LIKE '%" + keyword + "%' COLLATE NOCASE")
    persons = c.fetchall()
    for person in persons:
        results.append(itemPerson(person, c))

    c.execute("SELECT * FROM universities WHERE name LIKE '%" + keyword + "%' COLLATE NOCASE")
    univs = c.fetchall()
    c.execute("SELECT * FROM universities WHERE nameabbr LIKE '" + keyword + "' COLLATE NOCASE")
    univs = list(set(univs + c.fetchall()))
    for univ in univs:
        item = dict(zip(["Name", "Abbr", "NameAbbr", "CSRank", "AIRank", \
                "PLRank", "SystemRank", "TheoryRank", \
                "NumACMFellow", "NumIEEEFellow", "NumFunding"], list(univ)))
        item.update({"isUniversity": "True"})
        results.append(item)

    for univ in univs:
        c.execute("SELECT * FROM persons WHERE univabbr='" + univ[1] + "'")
        persons = c.fetchall()
        for person in persons:
            results.append(itemPerson(person, c))

    # TODO
    words = keyword.strip().split(' ')

    # Select to render
    total = len(results)
    pageInfo = {
        "totalPage": str((total + pageLen - 1) / pageLen), \
        "curPage": page \
    }
    print pageInfo
    curPage = int(page)
    items = results[(curPage - 1) * pageLen : curPage * pageLen]
    print items
    return (pageInfo, items)
