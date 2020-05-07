import requests
from datetime import date
import xml.etree.ElementTree as ET
'''
通过接口读取json数据，先保存到本地.json文件中，再提取并导出成csv
'''

searchURLModel = "http://export.arxiv.org/api/query?search_query=all:COVID-19+OR+all:coronavirus+OR+all:sars-cov&" \
                 "sortBy=lastUpdatedDate&sortOrder=descending&start={}&max_results={}"

todayStr = date.today().strftime("%Y-%m-%d")

ns = {
    "openSearch": "http://a9.com/-/spec/opensearch/1.1/",
    "defaultNs": "http://www.w3.org/2005/Atom"
}


def getOne(start: int, numberPerQuery: int, fieldSeparator: str = '\t', lineSeparator: str = '\n') -> bytes:

    rawData: bytes = requests.get(searchURLModel.format(start, numberPerQuery)).content
    xmlDoc = ET.fromstring(rawData)
    totalCount = xmlDoc.find(".//openSearch:totalResults", ns).text
    dataList = []
    for entry in xmlDoc.findall("defaultNs:entry", ns):
        lineData = [todayStr, repr(entry.find("defaultNs:title", ns).text),
                    repr(entry.find('defaultNs:summary', ns).text),
                    entry.find('defaultNs:updated', ns).text, "None", entry.find('defaultNs:id', ns).text]
        dataList.append((fieldSeparator.join(lineData) + lineSeparator).encode(encoding='utf-8'))
    return int(totalCount), dataList


csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]


def process(outputFilePath: str = f'../outputcsv/{todayStr}', fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    try:
        print("arxiv start ---------:")
        with open(f'{outputFilePath}/arxiv.csv', 'wb') as outFile:
            # header
            outFile.write((fieldSeparator.join(csvHeaders) + lineSeparator).encode('utf-8'))
            num = 100
            # 第一次
            totalCount, dataList = getOne(0, num)
            outFile.writelines(dataList)
            if totalCount > num:
                for start in range(num, totalCount, num):
                    totalCount, dataList = getOne(start, num)
                    outFile.writelines(dataList)
        print("arxiv end ---------:")
    except Exception as e:
        print(f"arxvi failed : {e}")

# if __name__ == '__main__':
#     process()
