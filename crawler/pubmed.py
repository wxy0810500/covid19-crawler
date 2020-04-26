from datetime import date
from pymed.api import PubMed


csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]
todayStr = date.today().strftime("%Y-%m-%d")


def getRecords(queryRet, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    for article in queryRet:
        if article.doi is None:
            continue
        try:
            sourceLink = f"https://www.ncbi.nlm.nih.gov/pubmed/{article.pubmed_id}"
            dateStr = article.publication_date.strftime("%Y-%m-%d")
            record = [todayStr, article.title, repr(article.abstract) if article.abstract else "None",
                      dateStr, article.doi, sourceLink]
            yield (fieldSeparator.join(record) + lineSeparator).encode()
        except Exception as e:
            print(record)
            raise e


def process(outFile: str, queryStr: str, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    pubmed = PubMed(tool="MyTool", email="my@email.address")
    # get total count
    totalCount = pubmed.getTotalResultsCount(queryStr)
    print(f'totalCount : {totalCount} of query : {repr(queryStr)}')
    if totalCount == 0:
        return

    # Execute the query against the API.
    results = pubmed.query(queryStr, max_results=1000)

    records = getRecords(results, fieldSeparator, lineSeparator)

    with open(outFile, 'wb') as f:
        f.write((fieldSeparator.join(csvHeaders) + lineSeparator).encode())
        f.writelines(records)


def fetchLastSeveralDays(outFilePath: str = '../outputcsv', days: int = 1,
                         fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    queryStr = f'(((COVID-19) OR SARS-CoV-2) OR novel coronavirus) OR 2019-nCoV AND ("last {days} days"[PDat] )'
    outFile = outFilePath + f'/pubmed-{todayStr}-last_{days}_days.csv'
    print(f"fetch last {days} days")
    process(outFile, queryStr, fieldSeparator, lineSeparator)


def fetchLastSeveralYears(outFilePath: str = '../outputcsv', years: int = 1,
                          fieldSeparator: str = '\t', lineSeparator: str = '\n'):
    queryStr = f'(((COVID-19) OR SARS-CoV-2) OR novel coronavirus) OR 2019-nCoV AND ("last {years} years"[PDat] )'
    outFile = outFilePath + f'/pubmed-{todayStr}-last_{years}_years.csv'
    print(f"fetch last {years} years")
    process(outFile, queryStr, fieldSeparator, lineSeparator)


# if __name__ == '__main__':
#     # fetchLastSeveralYears(1)
#     # fetchLastSeveralDays(1)
#     pass
