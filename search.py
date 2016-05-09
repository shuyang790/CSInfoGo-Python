

def getItems(keyword, page):
    pageInfo = {
        "totalPage": "2", \
        "curPage": page \
    }
    items = [{
        "Name": "Bill Dally", \
        "University": "Stanford University", \
        "CSRank": "1", \
        "Funding": "Yes", \
        "IEEEFellow": "No", \
        "ACMFellow": "Yes"
        }]
    return (pageInfo, items)
