import json
from datetime import date
from multiprocessing import Pool, cpu_count, current_process

import pandas as pd
import requests
from requests.adapters import HTTPAdapter


from utils.proxy_ip_pool import getProxyURL, USER_AGENT
from utils.timeUtils import randomSleep

DOWNLOAD_URL = "https://docs.google.com/spreadsheets/d/1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw/export" \
               "?format=csv&id=1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw&gid=1470772867"

todayStr = date.today().strftime("%Y-%m-%d")

requests.adapters.DEFAULT_RETRIES = 5


def downLoadCsv(sourceFilePath: str):
    proxy = {
        "https": getProxyURL()
        # "https": "112.95.23.136:8888"
    }
    s = requests.Session()
    adapter = HTTPAdapter(max_retries=5)
    s.mount('https://', adapter)
    s.proxies = proxy
    s.keep_alive = False
    s.headers = {"User-Agent": USER_AGENT}
    r = s.get(DOWNLOAD_URL, timeout=500)
    sourceFile = f"{sourceFilePath}/raw-dimensions.csv"
    with open(sourceFile, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return sourceFile


def getAbstract(pubId: str, proxy: dict):
    resp = requests.get(f'https://app.dimensions.ai/details/sources/publication/{pubId}/abstract.json', proxies=proxy)
    if resp.status_code == 200:
        body = resp.content.decode()
        if body is not None:
            jsonObj = json.loads(body)
            try:
                return repr(jsonObj["docs"][0]["abstract"])
            except Exception as e:
                print(f'dimension-getAbstract failed. url:{pubId}, e:{e}')
                return None
        else:
            return None


csvHeaders = ["data_add", "title", "abstract", "Publication_date", "doi", "source_link"]


def doExtractDataTask(sourceDF: pd.DataFrame) -> pd.DataFrame:
    print(current_process().pid)
    pidS: pd.Series = sourceDF['Publication ID']
    pIdAndAbsDictList = []
    proxy = {
        "https": getProxyURL()
    }
    for index, pubId in pidS.iteritems():
        if index % 20 == 0:
            proxy = {
                "https": getProxyURL()
            }
        if index % 3 == 0:
            randomSleep(1)
        if index % 10 == 0:
            randomSleep(3)
        pIdAndAbsDictList.append({'Publication ID': pubId, 'abstract': getAbstract(pubId, proxy)})

    absDF = pd.DataFrame(pIdAndAbsDictList, columns=['Publication ID', 'abstract'])
    retDF = sourceDF.merge(absDF, how='left', on='Publication ID')
    return retDF


def extractData(sourceDF: pd.DataFrame):
    totalCount = len(sourceDF)
    print(f"get extra data : {totalCount}")

    if totalCount <= 100:
        return doExtractDataTask(sourceDF)
    elif totalCount <= 500:
        processCount = 4
    else:
        processCount = max(8, cpu_count())
    queueMaxLen = max(100, (totalCount//100 + 1))
    args = [sourceDF.iloc[i: i + 100] for i in range(0, totalCount, 100)]
    with Pool(processCount) as mp:
        results = mp.map(doExtractDataTask, args)

        retDF = results[0]
        for subRetDF in results[1:]:
            retDF = pd.concat([retDF, subRetDF], ignore_index=True)

    return retDF


def processLatestParts(sourceFile, preSourceFile, outFile, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    rawDF = pd.read_csv(sourceFile, sep=",",
                        usecols=['Publication ID', 'Date added', 'Title', 'Publication Date', 'DOI', 'Dimensions URL'])
    preRawDF = pd.read_csv(preSourceFile, sep=",",
                           usecols=['Publication ID', 'Date added', 'Title', 'Publication Date', 'DOI', 'Dimensions URL'])
    sDF = pd.concat([rawDF, preRawDF])
    sDF.drop_duplicates(subset='Publication ID', keep=False, inplace=True)
    retDF = extractData(sDF)
    retDF.to_csv(outFile, sep=fieldSeparator, line_terminator=lineSeparator, header=csvHeaders,
                 columns=['Date added', 'Title', 'abstract', 'Publication Date', 'DOI', 'Dimensions URL'])


def process_today(preSourceFile, outputFileDir: str = '../outputcsv', sourceFileDir: str = '../sourceFiles',
                  fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    sourceFile = downLoadCsv(sourceFileDir)
    # sourceFile = '../sourceFiles/raw-dimensions.csv'
    # outFile = f'{outputFileDir}/dimension_ai-{todayStr}.csv'
    # processLatestParts(sourceFile, preSourceFile, outFile,
    #                    fieldSeparator, lineSeparator)


if __name__ == '__main__':
    process_today('../sourceFiles/raw-dimension_ai_20200413.csv')
