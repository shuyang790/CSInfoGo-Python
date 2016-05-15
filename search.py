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
        "Identity": "Person" + item["UniversityAbbr"] + item["Name"].replace(' ', '_'), \
         })
    return item

def itemUniv(univ, c):
    item = dict(zip(["Name", "Abbr", "NameAbbr", "CSRank", "AIRank", \
            "PLRank", "SystemRank", "TheoryRank", \
            "NumACMFellow", "NumIEEEFellow", "NumFunding"], \
            list([x  if x != 'unknown' else '' for x in univ])))
    item.update({"isUniversity": "True"})
    return item

def calcScorePerson(item, keyword):
    words = keyword.split(' ')
    nameCover = float(len([1 for x in words if x in item['Name']])) / len(words)
    univCover = 1 if item['UniversityAbbr'] in words else 0
    validCover = float(len([1 for x in words if not x in item['Name'] \
                        and not x == item['UniversityAbbr']])) / len(words)
    importance = 1 if item['Title'].lower() == 'professor' else \
                    0.5 if item['Title'].lower() == 'associate professor' else 0
    return (nameCover + univCover + validCover) * 10 + importance

def calcScoreUniv(item, keyword):
    words = keyword.lower().replace('university', '').split(' ')
    nameCover = float(len([1 for x in words if x in item['Name']])) / len(words)
    validCover = float(len([1 for x in words if not x in item['Name'] \
                        and not x == item['NameAbbr']])) / len(words)
    ranking = float(80 - int(item['CSRank'])) / 80
    return ((nameCover + validCover) * 10 + ranking) * 10

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
    keyword = keyword.lower().strip()


    words = keyword.split(' ')

    c = conn.cursor()

    for word in words:
        c.execute("SELECT * FROM persons WHERE name LIKE '%" + word + "%' COLLATE NOCASE")
        persons = c.fetchall()
        for person in persons:
            it = itemPerson(person, c)
            if not it in results:
                results.append(it)
        if word == 'university':
            continue
        c.execute("SELECT * FROM universities WHERE name LIKE '%" + word + "%' COLLATE NOCASE")
        univs = c.fetchall()
        c.execute("SELECT * FROM universities WHERE nameabbr LIKE '" + word + "' COLLATE NOCASE")
        univs = list(set(univs + c.fetchall()))
        for univ in univs:
            results.append(itemUniv(univ, c))
            c.execute("SELECT * FROM persons WHERE univabbr='" + univ[1] + "'")
            persons = c.fetchall()
            for person in persons:
                results.append(itemPerson(person, c))

    for univ in univs:
        c.execute("SELECT * FROM persons WHERE univabbr='" + univ[1] + "'")
        persons = c.fetchall()
        for person in persons:
            results.append(itemPerson(person, c))
    conn.close()

    for item in results:
        if 'isPerson' in item:
            item.update({'Score': calcScorePerson(item, keyword)})
        if 'isUniversity' in item:
            item.update({'Score': calcScoreUniv(item, keyword)})

    results = sorted(results, cmp=\
            lambda x,y: -1 if y['Score'] < x['Score'] else 1)

    print results[:20]

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
