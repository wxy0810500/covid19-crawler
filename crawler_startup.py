import argparse

from crawler.arxiv import process as arxiv_pro
from crawler.biorxiv import process as biorxiv_pro
from crawler.chemrxiv import queryAllUpToNow as chemrxiv_all
from crawler.chemrxiv import querySinceToday as chemrxiv_today
from crawler.meta import SearchByKeyWords, FetchByFeed
from crawler.pubmed import fetchLastSeveralYears, fetchLastSeveralDays

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="download data from specific websites")
    argparser.add_argument('-t', dest='type', default='today', choices=['today', 'upToNow'], type=str)
    argparser.add_argument('-o', dest='outputFilePath', default='./', type=str, help="output file path")
    argparser.add_argument('-ro', dest='sourceFilePath', default='./', type=str, help="raw file path")
    argparser.add_argument('-fs', dest='fieldSeparator', default='\t', type=str, help="field separator")
    argparser.add_argument('-ls', dest='lineSeparator', default='\n', type=str, help="line separator")
    inputArgs = argparser.parse_args()
    optType = inputArgs.type
    sourceFilePath = inputArgs.sourceFilePath
    outputFilePath = inputArgs.outputFilePaht
    fieldSeparator = inputArgs.fieldSeparator
    lineSeparator = inputArgs.lineSeparator
    if "upToNow" == optType:
        # arxiv
        arxiv_pro(outputFilePath, fieldSeparator, lineSeparator)
        # biorxiv
        biorxiv_pro(outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
        # chemrxiv
        chemrxiv_all(outputFilePath, fieldSeparator, lineSeparator)
        # meta
        SearchByKeyWords.fetchAllByKeys(outputFilePath, 100, fieldSeparator, lineSeparator)
        # pubmed
        fetchLastSeveralYears(outputFilePath, 1, fieldSeparator, lineSeparator)
    elif 'today' == optType:
        # arxiv
        arxiv_pro(outputFilePath, fieldSeparator, lineSeparator)
        # biorxiv
        biorxiv_pro(outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
        # chemrxiv
        chemrxiv_today(outputFilePath, fieldSeparator, lineSeparator)
        # meta
        FetchByFeed.fetchYesterday(outputFilePath, fieldSeparator, lineSeparator)
        # pubmed
        fetchLastSeveralDays(outputFilePath, 1, fieldSeparator, lineSeparator)
    else:
        print("invalid type argument!")
