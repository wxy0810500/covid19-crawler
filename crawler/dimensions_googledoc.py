import requests
from datetime import date
import csv

DOWNLOAD_URL = "https://docs.google.com/spreadsheets/d/1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw/export" \
               "?format=csv&id=1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw&gid=1470772867"

todayStr = date.today().strftime("%Y-%m-%d")


def downLoadCsv(sourceFilePath: str):
    r = requests.get(DOWNLOAD_URL)
    sourceFile = sourceFilePath + f"/raw-dimensions-{todayStr}.csv"
    with open(sourceFile, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    return sourceFile


csvHeaders = ["data_add", "title", "abstract", "Publication_date", "doi", "source_link"]


def switchCsv(sourceFile, outputFile, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    with open(sourceFile, 'r', encoding='utf-8') as sf, open(outputFile, 'wb') as of:
        sourceReader = csv.reader(sf, delimiter=",")
        of.write(f'{fieldSeparator.join(csvHeaders)}{lineSeparator}'.encode())
        for sourceLine in sourceReader:
            # $0,$7,$6,$11,$2,$29
            newLine = f'{fieldSeparator.join([sourceLine[0], repr(sourceLine[7]), repr(sourceLine[6]), sourceLine[11], sourceLine[2], sourceLine[29]])}{lineSeparator}'
            of.write(newLine.encode())


def process(outputFileDir='../outputcsv', sourceFileDir='../sourceFiles',
            fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    # source = "../sourceFiles/raw-dimensions-2020-04-30.csv"
    switchCsv(downLoadCsv(sourceFileDir), f'{outputFileDir}/dimension_ai-{todayStr}-upToNow.csv',
              fieldSeparator, lineSeparator)
    # switchCsv(source, f'{outputFileDir}/dimension_ai-{todayStr}-upToNow.csv',
    #           fieldSeparator, lineSeparator)


if __name__ == '__main__':
    process()
