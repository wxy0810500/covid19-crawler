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
    argparser.add_argument('-o', dest='outputFilePath', default='../outputcsv/', type=str, help="output file path")
    argparser.add_argument('-ro', dest='sourceFilePath', default='../sourceFiles/', type=str, help="raw file path")
    argparser.add_argument('-fs', dest='fieldSeparator', default='\t', type=str, help="field separator")
    argparser.add_argument('-ls', dest='lineSeparator', default='\n', type=str, help="line separator")
    inputArgs = argparser.parse_args()
    optType = inputArgs.type
    sourceFilePath = inputArgs.sourceFilePath
    outputFilePath = inputArgs.outputFilePath
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
        try:
            print("meta start ---------:")
            SearchByKeyWords.fetchAllByKeys(outputFilePath, 100, fieldSeparator, lineSeparator)
            print("meta end ---------:")
        except Exception as e:
            print(f"meta failed : {e}")
        # pubmed
        try:
            print("pubmed start ---------:")
            fetchLastSeveralYears(outputFilePath, 1, fieldSeparator, lineSeparator)
            print("pubmed end ---------:")
        except Exception as e:
            print(f"pubmed failed : {e}")
    elif 'today' == optType:
        # arxiv
        arxiv_pro(outputFilePath, fieldSeparator, lineSeparator)
        # biorxiv
        biorxiv_pro(outputFilePath, sourceFilePath, fieldSeparator, lineSeparator)
        # chemrxiv
        chemrxiv_today(outputFilePath, fieldSeparator, lineSeparator)
        # meta
        try:
            print("meta start ---------:")
            # FetchByFeed.fetchYesterday(outputFilePath, fieldSeparator, lineSeparator)
            print("meta end ---------:")
        except Exception as e:
            print(f"meta failed : {e}")
        # pubmed
        try:
            print("pubmed start ---------:")
            # fetchLastSeveralDays(outputFilePath, 2, fieldSeparator, lineSeparator)
            print("pubmed end ---------:")
        except Exception as e:
            print(f"pubmed failed : {e}")
    else:
        print("invalid type argument!")
