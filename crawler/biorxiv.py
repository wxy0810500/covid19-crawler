import requests
import ijson
from datetime import date
'''
通过接口读取json数据，先保存到本地.json文件中，再提取并导出成csv
'''

jsonUrl = "https://connect.biorxiv.org/relate/collection_json.php?grp=181"
todayStr = date.today().strftime("%Y-%m-%d")


def downloadJsonToFile(downloadFilePath) -> str:
    r = requests.get(url=jsonUrl)
    downloadFile = downloadFilePath + f"/biorxiv-{todayStr}.json"
    with open(downloadFile, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return downloadFile


# {
#     "rel_title": title,
#     "rel_doi": doi,
#     "rel_link": source_link,
#     "rel_abs": abstract,
#     "rel_authors":
#     "rel_date": publication date,
#     "rel_site": site
# }
csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]


def switchToCsv(downloadFile, outputFilePath,
                fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    with open(outputFilePath + f"/biorxiv-{todayStr}-upToNow.csv", 'wb') as outFile:
        # header
        outFile.write((fieldSeparator.join(csvHeaders) + lineSeparator).encode('utf-8'))
        with open(downloadFile, "r") as sf:
            rels = ijson.items(sf, 'rels.item')
            for rel in rels:
                record = [todayStr, repr(rel['rel_title']), repr(rel['rel_abs']),
                          rel['rel_date'], repr(rel['rel_doi']), rel['rel_link']]
                outFile.write((fieldSeparator.join(record) + lineSeparator).encode('utf-8'))


def process(outputFilePath: str = "../outputcsv", downloadFilePath: str = "../souceFiles"
            , fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    switchToCsv(downloadJsonToFile(downloadFilePath), outputFilePath, fieldSeparator, lineSeparator)


if __name__ == '__main__':
    process()
