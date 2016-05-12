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
    item = dict(zip(["Name", "UniversityAbbr", "URL", "Title", "ResearchInterests",\
            "ACMFellow", "IEEEFellow", "Funding"], \
            list(person)))
    indices = [0] + [x+1 for x in range(len(item["Name"])) if not item["Name"][x].isalpha()]
    item["Name"] = ''.join([item["Name"][i].lower() if not i in indices \
                            else item["Name"][i].upper() \
                                for i in range(len(item["Name"]))])
    _univ = c.execute("SELECT * FROM universities WHERE Abbr='" + item["UniversityAbbr"] + "'")\
        .fetchall()[0]
    univ = [x if x != 'unknown' else '' for x in _univ]
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

def itemUniv(univ, c):
    item = dict(zip(["Name", "Abbr", "NameAbbr", "CSRank", "AIRank", \
            "PLRank", "SystemRank", "TheoryRank", \
            "NumACMFellow", "NumIEEEFellow", "NumFunding"], \
            list([x  if x != 'unknown' else '' for x in univ])))
    item.update({"isUniversity": "True"})
    return item

def getItems(keyword, page):

    if not os.path.isfile("./data/csinfo.db"):
        print "Cannot find database file, re-constructing ..."
        sys.stdout.flush()
        initDB.main()
        print "Database constructed!"
        sys.stdout.flush()

    global conn
    conn = sqlite3.connect("./data/csinfo.db")

    results = []
    keyword = keyword.strip()

    # TODO
    words = keyword.strip().split(' ')

    c = conn.cursor()

    for word in words:
        c.execute("SELECT * FROM persons WHERE name LIKE '%" + word + "%' COLLATE NOCASE")
        persons = c.fetchall()
        for person in persons:
            it = itemPerson(person, c)
            if not it in results:
                results.append(it)

    c.execute("SELECT * FROM universities WHERE name LIKE '%" + keyword + "%' COLLATE NOCASE")
    univs = c.fetchall()
    c.execute("SELECT * FROM universities WHERE nameabbr LIKE '" + keyword + "' COLLATE NOCASE")
    univs = list(set(univs + c.fetchall()))
    for univ in univs:
        results.append(itemUniv(univ, c))

    for univ in univs:
        c.execute("SELECT * FROM persons WHERE univabbr='" + univ[1] + "'")
        persons = c.fetchall()
        for person in persons:
            results.append(itemPerson(person, c))

    # Select to render
    total = len(results)
    pageInfo = {
        "totalPage": str((total + pageLen - 1) / pageLen), \
        "curPage": page \
    }
    print pageInfo
    curPage = int(page)
    items = results[(curPage - 1) * pageLen : curPage * pageLen]
    return (pageInfo, items)
