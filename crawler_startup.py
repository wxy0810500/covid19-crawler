import argparse
import os
import sys

from crawler.arxiv import process as arxiv_pro
from crawler.biorxiv import process as biorxiv_pro
from crawler.chemrxiv import queryAllUpToNow as chemrxiv_all
from crawler.chemrxiv import querySinceToday as chemrxiv_today
from crawler.meta import SearchByKeyWords, FetchByFeed
from crawler.pubmed import fetchLastSeveralYears, fetchLastSeveralDays


def crawlerWithoutType(sourceSite, outputFilePath, sourceFilePath, fieldSeparator, lineSeparator):
    if sourceSite is None or sourceSite == 'arxiv':
        # arxiv
        arxiv_pro(outputFilePath, fieldSeparator, lineSeparator)

    if sourceSite is None or sourceSite == 'biorxiv':
        # biorxiv
        biorxiv_pro(outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
        # dimension_ai


if __name__ == '__main__':

    currentPath = os.path.dirname(os.path.abspath(__file__))
    argparser = argparse.ArgumentParser(description="download data from specific websites")
    argparser.add_argument('-t', dest='type', default='lastDay', choices=['lastDay', 'upToNow'], type=str)
    argparser.add_argument('-s', dest='source', default=None,
                           choices=['arxiv', 'biorxiv', 'chemrxiv', 'dim_ai', 'meta', 'pubmed'])
    argparser.add_argument('-o', dest='outputFilePath', default=currentPath + '/outputcsv',
                           type=str, help="output file path")
    argparser.add_argument('-ro', dest='sourceFilePath', default=currentPath + '/sourceFiles',
                           type=str, help="raw file path")
    argparser.add_argument('-fs', dest='fieldSeparator', default='\t', type=str, help="field separator")
    argparser.add_argument('-ls', dest='lineSeparator', default='\n', type=str, help="line separator")
    inputArgs = argparser.parse_args()
    optType = inputArgs.type
    sourceSite = inputArgs.source
    sourceFilePath = inputArgs.sourceFilePath
    outputFilePath = inputArgs.outputFilePath
    fieldSeparator = inputArgs.fieldSeparator
    lineSeparator = inputArgs.lineSeparator
    if "upToNow" == optType:
        print("crawling all data up to now")
        crawlerWithoutType(sourceSite, outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
        if sourceSite is None or sourceSite == "chemrxiv":
            # chemrxiv
            try:
                chemrxiv_all(outputFilePath, fieldSeparator, lineSeparator)
            except Exception as e:
                print(f"chemrxiv failed : {e}")
        if sourceSite is None or sourceSite == "meta":
            # meta
            try:
                print("meta start ---------:")
                SearchByKeyWords.fetchAllByKeys(outputFilePath, 100, fieldSeparator, lineSeparator)
                print("meta end ---------:")
            except Exception as e:
                print(f"meta failed : {e}")
        if sourceSite is None or sourceSite == "pubmed":
            # pubmed
            try:
                print("pubmed start ---------:")
                fetchLastSeveralYears(outputFilePath, 1, fieldSeparator, lineSeparator)
                print("pubmed end ---------:")
            except Exception as e:
                print(f"pubmed failed : {e}")
    elif 'today' == optType:
        print("crawling last day's data")
        crawlerWithoutType(sourceSite, outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
        if sourceSite is None or sourceSite == "chemrxiv":
            # chemrxiv
            try:
                chemrxiv_today(outputFilePath, fieldSeparator, lineSeparator)
            except Exception as e:
                print(f"chemrxiv failed : {e}")
        if sourceSite is None or sourceSite == "meta":
            # meta
            try:
                print("meta start ---------:")
                FetchByFeed.fetchYesterday(outputFilePath, fieldSeparator, lineSeparator)
                print("meta end ---------:")
            except Exception as e:
                print(f"meta failed : {e}")
        if sourceSite is None or sourceSite == "pubmed":
            # pubmed
            try:
                print("pubmed start ---------:")
                fetchLastSeveralDays(outputFilePath, 2, fieldSeparator, lineSeparator)
                print("pubmed end ---------:")
            except Exception as e:
                print(f"pubmed failed : {e}")
    else:
        print("invalid type argument!")
