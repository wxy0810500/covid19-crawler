"""
meta.org

一、全量获取

1.登陆，获取cookie中的Authorization

2.通过searchs/papers接口批量、循环读取对应主题下article列表的信息

二、每日增量获取

1.
"""
import os
import argparse
import time
import platform
from datetime import date
from enum import Enum
from multiprocessing import Pool
from urllib import request

import ijson
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

todayStr = date.today().strftime("%Y-%m-%d")
csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]


def formatDate(pubDateStamp):
    if pubDateStamp is not None:
        pubDate = date.fromtimestamp(pubDateStamp / 1000).strftime("%Y-%m-%d")
    else:
        pubDate = todayStr
    return pubDate


def login():
    url = "https://www.meta.org/account/login"
    # 引入chromedriver.exe
    sysStr = platform.system().lower()
    if sysStr == "linux":
        chromeDriver = "/home/ghddiai/soft/chromedriver"
    elif sysStr == 'windows':
        chromeDriver = 'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'
    else:
        # 其他系统的直接报错，要求手动指定
        print("please set path of chromeDriver in crawler/chemrxiv.py!")
        chromeDriver = ''
    os.environ['webdriver.chrome.driver'] = chromeDriver

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    browser = webdriver.Chrome(chrome_options=chrome_options, executable_path=chromeDriver)
    browser.get(url)
    try:
        email = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.ID, r"email"))
        )
        email = browser.find_element_by_id("email")
        email.clear()
        email.send_keys('e_aidd@ghddi.org')
        passwd = browser.find_element_by_id('password')
        passwd.clear()
        passwd.send_keys('Ghddi@2020')
        while True:
            time.sleep(2)
            try:
                login_btn = browser.find_element_by_id(r'btn-login')
                login_btn.click()
            except NoSuchElementException:
                break

        WebDriverWait(browser, 60).until(
            EC.presence_of_element_located((By.XPATH, r"//h1[@data-rosetta-id]"))
        )
        cookies = browser.get_cookies()
        authorization = None
        for cookie in cookies:
            if cookie["name"] == "Authorization" and cookie["domain"] == "www.meta.org":
                authorization = cookie["value"]

    finally:
        browser.quit()
    return authorization


class SearchByKeyWords:
    __keys = ["\"COVID 19\"",
              "COVID-19",
              "2019-nCoV",
              "COVID19",
              "SARS-CoV-2"]
    __keyFormat = "t---{}"

    __urlTemp = "https://search-http.prod.meta-infra.org/amaunet/v2/search/papers" \
                "?articleTypes=preprint,journalArticle&order=asc&sortBy=paper_pub_date&page={}&pageSize={}"

    @classmethod
    def fetchAllByKeys(cls, outputFilePath: str = '../outputcsv',
                       pageSize: int = 100, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
        # authorization = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlEwVkVRa1JHUXpneVJUZEVSa0UzTjBVNVJrTTFNREF3TTBaRE5FSkVSREpHT1RWQ05UbEZOZyJ9.eyJodHRwczovL21ldGEub3JnL2dyb3VwcyI6W10sImlzcyI6Imh0dHBzOi8vbG9naW4ubWV0YS5vcmcvIiwic3ViIjoiYXV0aDB8NWU5OTYzNDMxYjMwZWMwYzg1YmExMmYyIiwiYXVkIjpbImh0dHBzOi8vYXBpLm1ldGEub3JnIiwiaHR0cHM6Ly9jemktbWV0YS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTg3NjEwMDk5LCJleHAiOjE1ODc2OTY0OTksImF6cCI6IlhNZEJrN3k4b2EzV1dKVjRIQWV5ZFZrcGNnSGlLb29jIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbInBsYWNlaG9sZGVyOm1lbWJlciIsInJlYWQ6dGhlbWF0aWNfZmVlZHMiXX0.ibGxfM-0fO4S0TDuPJq_NjS4AiJPb6_kRX8TLQe557SFvMa8Kwhcf43wKXqKCWSz3yIYllvDuJzBYhLyFau6NA3jmwsxjIq5O57AJqo2Ug10CMSk21gkwQks3UsIuQp7EYfj6--O4aaQbCEI4Yv6Octd4x7oWidhiqQR7eyEKq07Jpp_rWWsRWwD9SRpIxsL4ge7r1qLCMHPh8j9QIl0_x9qHQAGCzh9ROynWv8icv9-QwwicLJHKB078ue61zIesKTeKCiyqfqoMRl0J12CkTXM8dvMLzKJpP_4E8ux3CBqW8RhxWg_LkdelNEvL133s95XJ4OCxgDCgjfV3t6AnA"
        authorization = login()
        with Pool(4) as pool:
            pool.starmap(cls._searchByOneKeyWord,
                         ((authorization, cls.__keyFormat.format(key),
                           outputFilePath + "/meta-{}-{}-upToYesterday.csv".format(todayStr, index),
                           pageSize, fieldSeparator, lineSeparator)
                          for index, key in enumerate(cls.__keys)))
        outFile = f'{outputFilePath}/meta-{todayStr}-upToYesterday.csv'
        with open(outFile, 'wb') as f:
            f.write((fieldSeparator.join(csvHeaders) + lineSeparator).encode())

        os.system(f'cat {outputFilePath}/meta-{todayStr}-*-upToYesterday.csv > {outFile}')
        # for key in keys:
        #     searchByKeyWord(authorization, cls.__keyFormat.format(key),
        #                            outputFilePath + f"../outputcsv/meta-{todayStr}-{repr(key)}--upToYesterday.csv",
        #                            pageSize, fieldSeparator, lineSeparator)

    @classmethod
    def _getTotalCount(cls, body: dict, authorization: str, startDate: str = None, endDate: str = None):
        url = cls.__urlTemp.format(0, 1)
        if startDate is not None and endDate is not None:
            url = url + "&startDate={}&endDate={}".format(startDate, endDate)
        headers = {
            "Content-type": "application/json",
            "authorization": "Bearer {}".format(authorization)
        }
        req = request.Request(url, headers=headers, data=json.dumps(body).encode())
        resp = request.urlopen(req)
        result = json.loads(resp.read().decode())
        return int(result["data"]["_embedded"]["count"])

    @classmethod
    def _searchByOneKeyWord(cls, authorization: str, keyWord: str, outFile: str, pageSize: int = 100,
                            fieldSeparator: str = '\t', lineSeparator: str = '\n'):
        # print(authorization)
        searchBody = {"matching": [{"set": [keyWord]}]}
        # first
        totalCount = cls._getTotalCount(searchBody, authorization)
        print("search by key word : {} , total count = {}", repr(keyWord), totalCount)
        with open(outFile, "wb") as f:
            for page in range(0, totalCount // pageSize + 1):
                time.sleep(2)
                records = cls._searchOnePage(searchBody, authorization, page, pageSize,
                                             fieldSeparator, lineSeparator)
                if len(records) > 0:
                    f.writelines(records)
                    print("totalSize : {}. pageSize : {} --- write down page {}".format(totalCount, pageSize, page))

    @classmethod
    def _searchOnePage(cls, body: dict, authorization: str,
                       page: int = 0, pageSize: int = 100,
                       fieldSeparator: str = '\t', lineSeparator: str = '\n'):
        url = cls.__urlTemp.format(page, pageSize)
        headers = {
            "Content-type": "application/json",
            "authorization": "Bearer {}".format(authorization)
        }
        req = request.Request(url, headers=headers, data=json.dumps(body).encode())
        resp = request.urlopen(req)

        results = ijson.items(resp, "data.results.item")
        records = []
        if results is not None:
            for article in results:
                source_link = 'https://www.meta.org/papers/article/{}'.format(article["id"])
                records.append(
                    (
                            fieldSeparator.join(
                                [todayStr, repr(article["title"]), repr(article.get("abstract", "None")),
                                 formatDate(article["pubmedReleaseDate"]), article.get("doi", "None"), source_link]
                            ) + lineSeparator
                    ).encode()
                )

        return records


class FetchByFeed:
    _urlTemp = "https://feed-http.prod.meta-infra.org/feeds/v2/feeds/" \
              "{}/item-groups?byViewState={{byViewState}}&filterBy=preprint,journalArticle" \
              "&groupBy={}&group={}&page={}&pageSize={}"

    class GroupBy(Enum):
        DAILY = "daily"
        WEEKLY = "weekly"
        MONTHLY = "monthly"

    @classmethod
    def _getTotalCount(cls, authorization: str, feedId: str, groupBy: GroupBy, group: str = "1"):
        url = cls._urlTemp.format(feedId, groupBy.value, group, 1, 1)
        headers = {
            "authorization": "Bearer {}".format(authorization)
        }
        req = request.Request(url, headers=headers)
        resp = request.urlopen(req)
        result = json.loads(resp.read().decode())

        count = int(result["data"]["groups"][0]["count"])
        print("fetch by feedId, total count = {}".format(count))
        return count

    @classmethod
    def _fetchOnePage(cls, authorization: str, feedId: str, groupBy: GroupBy, group: str = '1',
                      page: int = 1, pageSize: int = 100, fieldSeparator: str = '\t', lineSeparator: str = '\n'):
        url = cls._urlTemp.format(feedId, groupBy.value, group, page, pageSize)
        headers = {
            "Authorization": "Bearer {}".format(authorization)
        }
        req = request.Request(url, headers=headers)
        resp = request.urlopen(req)
        # respBody = json.loads(resp.read().decode())
        # for item in respBody["data"]["groups"][0]["items"]:
        #     print(item)
        groups = ijson.items(resp, 'data.groups.item')
        records = []
        for group in groups:
            items = group["items"]
            for item in items:
                # csvHeaders = ["data_add", "title", "abstract", "Publication date", "doi", "source_link"]
                entity = item['target']['_embedded']['entity']
                source_link = 'https://www.meta.org/papers/article/{}'.format(str(entity["id"]))
                records.append(
                    (fieldSeparator.join(
                        [todayStr, repr(entity['title']), repr(entity.get("abstract", "None")),
                         formatDate(entity["pubmedReleaseDate"]), entity.get("doi", "None"), source_link]
                    ) + lineSeparator).encode()
                )
        return records

    @classmethod
    def _fetchPages(cls, outFile: str, authorization: object, feedId: object, groupBy: object, group: object = '1',
                    pageSize: object = 50, fieldSeparator: object = '\t', lineSeparator: object = '\n') -> object:
        """

        :param outFile:
        :param authorization:
        :param feedId:
        :param groupBy:
        :param group: 默认值为1，表示符合groupby条件的最近日期
        :param pageSize:
        :param fieldSeparator:
        :param lineSeparator:
        :return:
        """
        totalCount = cls._getTotalCount(authorization, feedId, groupBy, group)
        with open(outFile, "wb") as f:
            f.write((fieldSeparator.join(csvHeaders) + lineSeparator).encode())
            for page in range(0, totalCount // pageSize + 1):
                time.sleep(2)
                records = cls._fetchOnePage(authorization, feedId, groupBy, group, page, pageSize,
                                            fieldSeparator, lineSeparator)
                if len(records) > 0:
                    f.writelines(records)
                    print("fetch feed || totalSize : {}. pageSize : {} --- write down page {}".
                          format(totalCount, pageSize, page))

    @classmethod
    def fetchYesterday(cls, outputFilePath: str = '../outputcsv', fieldSeparator: str = '\t', lineSeparator: str = '\n'):
        outputFile = outputFilePath + f"/meta-{todayStr}-onlyYesterday.csv"
        # auth = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlEwVkVRa1JHUXpneVJUZEVSa0UzTjBVNVJrTTFNREF3TTBaRE5FSkVSREpHT1RWQ05UbEZOZyJ9.eyJodHRwczovL21ldGEub3JnL2dyb3VwcyI6W10sImlzcyI6Imh0dHBzOi8vbG9naW4ubWV0YS5vcmcvIiwic3ViIjoiYXV0aDB8NWU5OTYzNDMxYjMwZWMwYzg1YmExMmYyIiwiYXVkIjpbImh0dHBzOi8vYXBpLm1ldGEub3JnIiwiaHR0cHM6Ly9jemktbWV0YS5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTg3ODk3NTUwLCJleHAiOjE1ODc5ODM5NTAsImF6cCI6IlhNZEJrN3k4b2EzV1dKVjRIQWV5ZFZrcGNnSGlLb29jIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbInBsYWNlaG9sZGVyOm1lbWJlciIsInJlYWQ6dGhlbWF0aWNfZmVlZHMiXX0.hsU1w0RhD0h1QB7n8FJlKS-_tpHTjsl4w4ppEFq4tPPJPuvlD8WlfGk4TKZRwlT--V7Llc8YlbOoKOAdxRwAQYB8wWvlsSPehbQN5xYNVtW97WeMtg6leGahhkXxTgb1p15qA3AOPAWBEN8Yw38UaSyheVYZ4IDc6v7hLy4qTL0DrROntxeXwEtTTPo5_DuyAn7myA2m27B_rSfDIrF9_sCWTQMdgdjfL4qcP7FZxcwOXcywrvSr6qSRacB8ONnSgFtDEOsnuXpZY3tKEaXY4_sYwtEWo2EK0pTnumipjfCVdcPraoMnXk3_OJdAhGrK8uAaPTmrxmzALu0GZ2hnTQ"
        feedId = "e0bb0d63-ba7a-4b16-a92e-d0e406f9e437"
        auth = login()
        FetchByFeed._fetchPages(outputFile, auth, feedId, FetchByFeed.GroupBy.DAILY, "1", 50,
                                fieldSeparator, lineSeparator)


# if __name__ == '__main__':
#     argParser = argparse.ArgumentParser(description="get article base info from meta.")
#     argParser.add_argument('-type', required=True, type=str,
#                            choices=['yesterday', 'someday', 'allTime'],
#                            help='options: yesterday(yesterday only), someday(specified by arg:-date), '
#                                 'allTime(up to yesterday)')
#     argParser.add_argument('-date', default=None, type=str, help='optional arg, date format : YYYY-mm-DD')
#     args = argParser.parse_args()
#     optType = args.type
#     sDate = args.type
#     if 'yesterday' == optType:
#         FetchByFeed.fetchYesterday()
#     elif 'allTime' == optType:
#         SearchByKeyWords.fetchAllByKeys()
#     elif 'someday' == optType:
#         pass
#     else:
#         print("invalid 'type' value! options:yesterday, someday, allTime")
