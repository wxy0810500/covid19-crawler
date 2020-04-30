import requests
from datetime import date
import json

personal_token = "13149d1fe2dc5f561e09e2066424008230fdac3e98b6f3d" \
                 "21d535c309ad15eeb9525786abeae3f4e637020cc010587f2fa6657321424dba90715f6c8ab3d2b6e"
# post
searchURL = "https://api.figshare.com/v2/articles/search"
post_headers = {"authorization": "token",
                "Content-type": "application/json"}


def doPostQuery(queryParams):
    resp = requests.post(searchURL, json=queryParams, headers=post_headers)
    if resp.status_code == 200:
        body = resp.content.decode('utf-8')
        if body is not None:
            return json.loads(body)
        else:
            return None
    else:
        return None


def fetchOneArticleInfo(pubAPI: str):
    resp = requests.get(pubAPI)
    if resp.status_code == 200:
        body = resp.content.decode()
        if body is not None:
            return json.loads(body)
        else:
            return None
    else:
        return None


# {
#   "defined_type_name": "journal contribution",
#   "handle": "",
#   "url_private_html": "https://figshare.com/account/articles/12136032",
#   "timeline": {
#     "revision": "2020-04-16T09:29:38",
#     "firstOnline": "2020-04-16T09:29:38",
#     "posted": "2020-04-16T09:29:38"
#   },
#   "url_private_api": "https://api.figshare.com/v2/account/articles/12136032",
#   "url_public_api": "https://api.figshare.com/v2/articles/12136032",
#   "id": 12136032,
#   "doi": "10.6084/m9.figshare.12136032.v1",
#   "thumb": "https://s3-eu-west-1.amazonaws.com/pfigshare-u-previews/22316919/thumb.png",
#   "title": "Emerging Mental Health Issues from the Novel Coronavirus (COVID-19) Pandemic",
#   "url": "https://api.figshare.com/v2/articles/12136032",
#   "defined_type": 6,
#   "resource_title": "",
#   "url_public_html": "https://figshare.com/articles/Emerging_
#   Mental_Health_Issues_from_the_Novel_Coronavirus_COVID-19_Pandemic/12136032",
#   "resource_doi": "",
#   "published_date": "2020-04-16T09:29:38Z",
#   "group_id": null
# }
csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]
basicQueryParams = {
    "item_type": 6,
    "order": "published_date",
    "search_for": ":title:coronavirus OR :title:covid-19 OR :title:SARS-CoV-2",
    "order_direction": "desc"
}


def query(sinceToday: bool, outputFilePath: str,  fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    offset = 0
    limit = 100
    todayStr = date.today().strftime("%Y-%m-%d")
    queryParams = basicQueryParams.copy()
    queryParams["limit"] = limit
    if sinceToday:
        queryParams["published_since"] = todayStr
        outputFileName = outputFilePath + f'/chemrxiv-{todayStr}-today.csv'
    else:
        outputFileName = outputFilePath + f'/chemrxiv-{todayStr}-upToNow.csv'
    outputFile = open(outputFileName, "wb")
    outputFile.write((fieldSeparator.join(csvHeaders) + lineSeparator).encode())
    stop = False
    while stop is not True:
        try:
            queryParams["offset"] = offset
            articleList = doPostQuery(queryParams)
            if articleList is not None and len(articleList) > 0:
                for article in articleList:
                    # abstracht:通过url_public_api接口逐个读取文章信息，从返回值中提取description。
                    pubAPI = article["url_public_api"]
                    artInfo = fetchOneArticleInfo(pubAPI)
                    if artInfo is not None:
                        csvRecord = [todayStr, repr(article["title"]), repr(artInfo["description"]),
                                     article["published_date"], article["doi"], article["url_public_html"]]
                        outputFile.write((fieldSeparator.join(csvRecord) + lineSeparator).encode())
                print(f"chemrxiv offset : {offset} , article num : {len(articleList)}")
                if len(articleList) < limit:
                    stop = True
            offset += limit
        except Exception as e:
            statu_code = e.args[0]
            if statu_code is not None and type(statu_code) == int and int(statu_code) == 422:
                stop = True
            else:
                outputFile.close()
                raise Exception
    outputFile.close()


def querySinceToday(outputFilePath: str = '../outputcsv', fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    try:
        print("chemrxiv start ---------:")
        query(True, outputFilePath, fieldSeparator, lineSeparator)
        print("chemrxiv end ---------:")
    except Exception as e:
        print(f"chemrxiv failed {e}")


def queryAllUpToNow(outputFilePath: str = '../outputcsv', fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    try:
        print("chemrxiv start ---------:")
        query(False, outputFilePath, fieldSeparator, lineSeparator)
        print("chemrxiv end ---------:")
    except Exception as e:
        print(f"chemrxiv failed {e}")

#
# if __name__ == '__main__':
#     queryAllUpToNow()
