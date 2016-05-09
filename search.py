#*-encoding: utf-8 -*

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

allItems = []
pageLen = 10

univName2Abbr = {}
univAbbr2Name = {}

def init():
    for line in open("data/cs-overall-rank.txt", "r"):
        eles = line.split('|')
        eles[0] += '-'
        for ch in eles[1]:
            if ch.isupper():
                eles[0] += ch
        if (line.startswith("29|")):
            print "#" + eles[0] + "$" + eles[1].strip() + "#"
        univName2Abbr.update({eles[1].strip(): eles[0]})
    univName2Abbr.update({"University of Maryland-​College Park":"15-UMD"})
    univName2Abbr.update({"University of Minnesota-​Twin Cities":"29-UMN"})
    univName2Abbr.update({"Rutgers, The State University of New Jersey-​New Brunswick":"34-RU"})
    univName2Abbr.update({"University of Chicago":"34-UCH"})
    univName2Abbr.update({"Washington University in St. Louis":"40-WUSTL"})
    univName2Abbr.update({"University of Colorado-​Boulder":"40-UCOB"})
    univName2Abbr.update({"University of Utah":"40-UTA"})
    univName2Abbr.update({"University at Buffalo-​SUNY":"63-UBS"})
    #univName2Abbr.update({"":""})

    for name, abbr in univName2Abbr.iteritems():
        univAbbr2Name.update({abbr: name})

    for line in open("data/index.txt", "r"):
        eles = line.strip().split('|')
        rawName = eles[1].strip().split(' ')
        item = {
            "Name": ' '.join([w[0].upper() + w[1:].lower() \
                        for w in rawName if w != ""]), \
            "UniversityAbbr": eles[0], \
            "CSRank": eles[0].split('-')[0], \
            "University": univAbbr2Name[eles[0]], \
            "ACMFellow": "Yes" if eles[2] == "True" else "No", \
            "IEEEFellow": "Yes" if eles[3] == "True" else "No", \
            "Funding": "Yes" if eles[4] == "True" else "No", \
        }
        global allItems
        allItems.append(item)

def getItems(keyword, page):
    results = []
    for item in allItems:
        if item["Name"].upper().find(keyword.upper()) != -1 \
            or item["University"].upper().find(keyword.upper()) != -1 \
            or item["UniversityAbbr"].upper().find(keyword.upper()) != -1:
                results.append(item)

    total = len(results)
    pageInfo = {
        "totalPage": str((total + pageLen - 1) / pageLen), \
        "curPage": page \
    }
    curPage = int(page)
    items = results[(curPage - 1) * pageLen : curPage * pageLen]
    return (pageInfo, items)
