#*- encoding: utf-8 -*
import sqlite3
import os, sys

crawledDataDir = '../CSInfoCollector/data'

univName2Abbr = {}
univAbbr2Name = {}
univAbbr2ACM = {}
univAbbr2IEEE = {}
univAbbr2Fund = {}

def findall(text,s):
	res = []
	index = 0
	while ((text.find(s,index)) != -1):
		pos = text.find(s,index);
		res.append(pos)
		index = pos + 1
	return res

def judgefellow(text,s):
	pos = findall(text,'fellow')
	for p in pos:
		if s in text[p-15:p+15]:
			return True
	return False

def scanCrawledData():
    conn = sqlite3.connect("./data/csinfo.db")
    c = conn.cursor()

    for univ in os.listdir(crawledDataDir):
        if(univ.find('.') != -1):
            continue
        univDir = os.path.join(crawledDataDir, univ)

        for professor in os.listdir(univDir):
            if(professor.find('.') != -1):
                continue

            isAcmfellow = 0
            isIeeefellow = 0
            isGranted = 0


            professorDir = os.path.join(univDir, professor)

            if os.path.isfile(os.path.join(professorDir, "url.txt")):
                with open(os.path.join(professorDir, "url.txt"), "r") as f:
                    url = f.readlines()[0].strip()
            else:
                url="unknown"

            for info in os.listdir(professorDir):
                infopath = os.path.join(professorDir,info);
                if(os.path.isfile(infopath) == False):
                    continue

                webpage = open(infopath)
                text = webpage.read().lower()
                isAcmfellow += judgefellow(text,'acm')
                isIeeefellow += judgefellow(text,'ieee')
                isGranted += (text.find('nsf') or text.find('grant'))
                webpage.close()

            c.execute("INSERT INTO persons VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"\
                % ( professor.replace("'", "''").replace('-', '').replace(',', ''),\
                    univ, \
                    url, \
                    "unknown", \
                    "Yes" if isAcmfellow >= 1 else "No",\
                    "Yes" if isIeeefellow >= 1 else "No",\
                    "Yes" if isGranted >= 1 else "No",\
                ))

            if isAcmfellow >= 1:
                univAbbr2ACM[univ] += 1
            if isIeeefellow >= 1:
                univAbbr2IEEE[univ] += 1
            if isGranted >= 1:
                univAbbr2Fund[univ] += 1

    conn.commit()
    conn.close()

def readUnivNames():

    for line in open("data/cs-overall-rank.txt", "r"):
        eles = line.split('|')
        eles[0] += '-'
        for ch in eles[1]:
            if ch.isupper():
                eles[0] += ch
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
        univAbbr2ACM.update({abbr: 0})
        univAbbr2IEEE.update({abbr: 0})
        univAbbr2Fund.update({abbr: 0})

def readRanks(filename):
    ranks = {}
    for line in open(filename, "r"):
        num = line.split('|')[0].strip()
        name = line.split('|')[1].strip()
        ranks.update({name: num})
    return ranks

def addUnivInfo():
    conn = sqlite3.connect("./data/csinfo.db")
    c = conn.cursor()

    csranks = readRanks("./data/cs-overall-rank.txt")
    airanks = readRanks("./data/cs-artificial-intelligence-rank.txt")
    plranks = readRanks("./data/cs-programming-language-rank.txt")
    systemranks = readRanks("./data/cs-system-rank.txt")
    theoryranks = readRanks("./data/cs-theory-rank.txt")

    for name, abbr in univName2Abbr.iteritems():
        c.execute("INSERT INTO universities VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"\
            % ( name, \
                abbr, \
                abbr.split('-')[-1], \
                csranks[name], \
                airanks[name] if name in airanks else "unknown", \
                plranks[name] if name in plranks else "unknown", \
                systemranks[name] if name in systemranks else "unknown", \
                theoryranks[name] if name in theoryranks else "unknown", \
                str(univAbbr2ACM[univName2Abbr[name]]), \
                str(univAbbr2IEEE[univName2Abbr[name]]), \
                str(univAbbr2Fund[univName2Abbr[name]]) \
            ))

    conn.commit()
    conn.close()

def main():
    os.system("rm -rf data/csinfo.db")
    conn = sqlite3.connect("./data/csinfo.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE universities
                (name, abbr, nameabbr, csrank, airank, plrank, systemrank, theoryrank, numacmfellow, numieeefellow, numfunding)''')

    c.execute('''CREATE TABLE persons
                (name, univabbr, url, researchinterests, acmfellow, ieeefellow, funding)''')

    conn.commit()
    conn.close()

    readUnivNames()
    scanCrawledData()
    addUnivInfo()

if __name__ == "__main__":
    main()
