import argparse
import os
from datetime import date, timedelta
import pandas as pd
from typing import Callable

from crawler.arxiv import process as arxiv_pro
from crawler.biorxiv import process as biorxiv_pro
from crawler.chemrxiv import queryAllUpToNow as chemrxiv_all
from crawler.chemrxiv import querySinceToday as chemrxiv_lastDay
from crawler.meta import processAll as meta_all, processLastDay as meta_lastDay
from crawler.pubmed import processAll as pubmed_all, processLastDay as pubmed_lastDay
from crawler.dimensions_googledoc import process as dimension_pro


def getYesterday():
    yesterday = date.today() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def crawlerWithoutType(sourceSite, outputFilePath, sourceFilePath, fieldSeparator, lineSeparator):
    if sourceSite is None or sourceSite == 'arxiv':
        # arxiv
        arxiv_pro(outputFilePath, fieldSeparator, lineSeparator)

    if sourceSite is None or sourceSite == 'biorxiv':
        # biorxiv
        biorxiv_pro(outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)

    if sourceSite is None or sourceSite == 'dimension':
        # dimension_ai
        try:
            print("dimension start ---------:")
            dimension_pro(outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
            print("dimension end ---------:")
        except Exception as ex:
            print(f"dimension failed : {ex}")


def processLastDay(webSite: str, todayFunc: Callable, allFunc: Callable,
                   outputFilePath: str, fieldSeparator: str, lineSeparator: str):
    try:
        todayOutputFilePath = f'{outputFilePath}/{todayStr}'
        previousFile = f'{outputFilePath}/{yesterdayStr}/{webSite}.csv'
        todayTargetFile = f'{outputFilePath}/{todayStr}/{webSite}.csv'
        if os.path.exists(previousFile):
            print(f"{webSite} today start ---------:")
            outFile = todayFunc(todayOutputFilePath, fieldSeparator, lineSeparator)
            os.system(f'cat {outFile} {previousFile} > {todayTargetFile}')
            print(f"{webSite} today end ---------:")
        else:
            print(f"{webSite} all start ---------:")
            allFunc(todayOutputFilePath, fieldSeparator, lineSeparator)
            print(f"{webSite} all end ---------:")

    except Exception as pe:
        print(f"{webSite} failed : {pe}")


if __name__ == '__main__':

    todayStr = date.today().strftime("%Y-%m-%d")
    currentPath = os.path.dirname(os.path.abspath(__file__))
    argparser = argparse.ArgumentParser(description="download data from specific websites")
    argparser.add_argument('-t', dest='type', default='lastDay', choices=['lastDay', 'upToNow'], type=str)
    argparser.add_argument('-s', dest='source', default=None,
                           choices=['arxiv', 'biorxiv', 'chemrxiv', 'dimension', 'meta', 'pubmed'])
    argparser.add_argument('-o', dest='outputFilePath', default=f'{currentPath}/outputcsv',
                           type=str, help="output file path")
    argparser.add_argument('-ro', dest='sourceFilePath', default=f'{currentPath}/sourceFiles',
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
    todayOutputFilePath = f'{outputFilePath}/{todayStr}'
    todaySourceFilePath = f'{sourceFilePath}/{todayStr}'
    if os.path.exists(todaySourceFilePath) is False:
        os.makedirs(todaySourceFilePath)
    if os.path.exists(todayOutputFilePath) is False:
        os.makedirs(todayOutputFilePath)
    if "upToNow" == optType:
        print("crawling all data up to now")
        crawlerWithoutType(sourceSite, todayOutputFilePath, todaySourceFilePath, fieldSeparator, lineSeparator)
        if sourceSite is None or sourceSite == "chemrxiv":
            # chemrxiv
            try:
                chemrxiv_all(todayOutputFilePath, fieldSeparator, lineSeparator)
            except Exception as e:
                print(f"chemrxiv failed : {e}")
        if sourceSite is None or sourceSite == "meta":
            # meta
            try:
                print("meta start ---------:")
                meta_all(todayOutputFilePath, fieldSeparator, lineSeparator)
                print("meta end ---------:")
            except Exception as e:
                print(f"meta failed : {e}")
        if sourceSite is None or sourceSite == "pubmed":
            # pubmed
            try:
                print("pubmed start ---------:")
                pubmed_all(todayOutputFilePath, fieldSeparator, lineSeparator)
                print("pubmed end ---------:")
            except Exception as e:
                print(f"pubmed failed : {e}")
    elif 'lastDay' == optType:
        print("crawling last day's data")
        crawlerWithoutType(sourceSite, todayOutputFilePath, todaySourceFilePath, fieldSeparator, lineSeparator)
        yesterdayStr = getYesterday()
        if sourceSite is None or sourceSite == "chemrxiv":
            # chemrxiv
            processLastDay('chemrxiv', chemrxiv_lastDay, chemrxiv_all, outputFilePath, fieldSeparator, lineSeparator)
        if sourceSite is None or sourceSite == "meta":
            # meta
            processLastDay('meta', meta_lastDay, meta_all, outputFilePath, fieldSeparator, lineSeparator)
        if sourceSite is None or sourceSite == "pubmed":
            # pubmed
            processLastDay('pubmed', pubmed_lastDay, pubmed_all, outputFilePath, fieldSeparator, lineSeparator)
    else:
        print("invalid type argument!")
