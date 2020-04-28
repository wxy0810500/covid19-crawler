import requests
import json
from datetime import date
from typing import List


todayStr = date.today().strftime("%Y-%m-%d")
HOST = "https://app.dimensions.ai"


def getAbstract(url: str):
    resp = requests.get(f'{HOST}{url}')
    if resp.status_code == 200:
        body = resp.content.decode('utf-8')
        if body is not None:
            jsonObj = json.loads(body)
            try:
                return repr(jsonObj["docs"][0]["abstract"])
            except Exception as e:
                print(f'dimension-getAbstract failed. url:{url}, e:{e}')
                return None
        else:
            return None


def getResultList(cursor: str = None):
    url = 'https://app.dimensions.ai/discover/publication/results.json' \
          '?search_text="2019-nCoV" OR "COVID-19" OR "SARS-CoV-2" OR "HCoV-2019" OR "hcov" OR "NCOVID-19" OR  ' \
          '"severe acute respiratory syndrome coronavirus 2" OR "severe acute respiratory syndrome corona virus 2"' \
          ' OR (("coronavirus"  OR "corona virus") AND (Wuhan OR China OR novel))' \
          '&search_type=kws&search_field=full_search&and_facet_year=2020'
    if cursor:
        url = f'{url}&cursor={cursor}'

    resp = requests.get(url)
    if resp.status_code == 200:
        body = resp.content.decode('utf-8')
        if body is not None:
            return json.loads(body)
        else:
            raise Exception(f"get result list failed:no response body")
    else:
        raise Exception(f"get result list failed")


csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]


def getCsvRecords(docList: List, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    for doc in docList:
        abstract = getAbstract(doc['navigation']['abstract_json'])
        yield (fieldSeparator.join(
            [todayStr, doc.get('title', "None"), abstract if abstract else "None", doc.get('pub_date', "None"),
             doc.get('doi', "None"), f'{HOST}{doc["navigation"]["path"]}']
        ) + lineSeparator).encode()


def process(outputFilePath: str = '../outputcsv', fieldSeparator: str = '\t', lineSeparator: str = '\n'):

    # first time
    listRet = getResultList()

    totalCount = listRet['count']
    print(f"totalCount : {totalCount}")
    if totalCount == 0:
        return
    outFile = f'{outputFilePath}/dimensionAI-{todayStr}-upToNow.csv'
    outF = open(outFile, 'wb')
    docs: List = listRet['docs']
    outF.writelines(getCsvRecords(docs, fieldSeparator, lineSeparator))

    cursor = listRet.get('next_cursor', None)
    try:
        while cursor:
            listRet = getResultList(cursor)
            docs: List = listRet['docs']
            outF.writelines(getCsvRecords(docs, fieldSeparator, lineSeparator))

            cursor = listRet.get('next_cursor', None)
    finally:
        outF.close()


if __name__ == '__main__':
    process()
