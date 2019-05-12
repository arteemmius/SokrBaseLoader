from parsel import Selector
import urllib3
import re
import itertools
import logging
import datetime

from Include.ReddisStorage import ReddisDataSaver


def getFullForm(selector):
    if selector.xpath('//p[@class="value"]/em').extract_first() is not None:
        #print(selector.xpath('//p[@class="value"]').extract_first())
        return re.sub(r'</p>', '', re.sub(r'</em>', '', re.sub(r'<em\s\S+">', '', re.sub(r'<p\s\S+>', '', selector.xpath('//p[@class="value"]').extract_first()))))
        """
        if selector.xpath('//p[@class="value"]/text()').extract_first() is not None:
            return selector.xpath('//p[@class="value"]/em[@class="got_morf"]/text()').extract_first() + selector.xpath('//p[@class="value"]/text()').extract_first()
        else:
            return selector.xpath('//p[@class="value"]/em[@class="got_morf"]/text()').extract_first()
        """
    else:
        return selector.xpath('//p[@class="value"]/text()').extract_first()


def getLabel(selector):
    #инициализиация labelss
    labels = ""
    if selector.xpath('//*[@class="comment"]/text()').extract_first() is not None:
        labels = selector.xpath('//*[@class="comment"]/text()').extract_first() + ","
    for i in range(0, len(selector.xpath('//*[@class="tag_list"]/span').extract())):
        if not "got_tag" in selector.xpath('//*[@class="tag_list"]/span').extract()[i]:
            #labels = labels + selector.xpath('//*[@class="tag_list"]/span/text()').extract()[i]
            labels = labels + re.sub(r'</span>', '', re.sub(r'<span\s\S+">', '', selector.xpath('//*[@class="tag_list"]/span').extract()[i]))
        else:
            #labels = labels + selector.xpath('//*[@class="tag_list"]/span/em/text()').extract()[i]
            labels = labels + \
            re.sub(r'</span>', '', re.sub(r'</em>', '', re.sub(r'<em\s\S+">', '', re.sub(r'<span\s\S+>', '', re.sub(r'<span\s\S+>', '', selector.xpath('//*[@class="tag_list"]/span').extract()[i])))))
    return labels


def getAbbr(selector):
    #рез-т поиска пуст
    if len(selector.xpath('//li/a').extract()) == 0:
        print("Empty <a></a> list!")
        exit(1)
    else:
        abr = ""
        for i in range(0, len(selector.xpath('//li/a').extract())):
            #print("i = " + str(i))
            if "visibility" in selector.xpath('//li/a').extract()[i]:
                continue
            elif not "em class" in selector.xpath('//li/a').extract()[i]:
                abr = abr + re.sub(r'</a>', '',re.sub(r'<a\s\S+">', '', selector.xpath('//a').extract()[i])) + " || "
            else:
                abr = abr + re.sub(r'</a>', '', re.sub(r'</em>', '', re.sub(r'<em\s\S+">', '', re.sub(r'<a\s\S+>', '',selector.xpath('//a').extract()[i]))))  + " || "
    return abr[0:len(abr) - 4]

alf = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
logging.basicConfig(filename="import.log", level=logging.INFO)
abbr = list()
inversAbbr = list()
for d in range(1, 3):
    abbr = abbr + list(itertools.combinations_with_replacement(alf, d))
for s in range(0, len(abbr)):
    abbr[s] = ''.join(abbr[s])
    if len(abbr[s]) == 2:
        if abbr[s][0] != abbr[s][1]:
            inversAbbr.append(abbr[s][::-1])
abbr = abbr + inversAbbr
label = list()
inputRedis = ReddisDataSaver()
http = urllib3.PoolManager()
for line in open('labels.txt', 'r', encoding='utf8'):
    label.append(line.replace('\n',''))
#abbr = ["А"]
#label = ["авиа"]
for j in range(0, len(abbr)):
    #print(abbr[j])
    logging.info(str(datetime.datetime.now()) + " >>> " +  abbr[j])
    for k in range(0, len(label)):
        request = http.request("GET", "http://sokr.ru/search/", fields={'abbr': abbr[j],'tag' : label[k]})
        sel = Selector(text = request.data.decode("utf-8"))
        #print(request.data.decode("utf-8"))
        #если поиск содержит минимум один результат, обрабатываем первый
        if sel.xpath('//tr[@class="search_results first"]').extract_first() is not None or sel.xpath('//tr[@class="search_results important first"]').extract_first() is not None:
            #logging.info(str(sel.xpath('//tr[@class="search_results first"]').extract_first()) + "\n")
            if sel.xpath('//tr[@class="search_results first"]').extract_first() is not None:
                firstBlock = Selector(text = str(sel.xpath('//tr[@class="search_results first"]').extract_first()))
            if sel.xpath('//tr[@class="search_results important first"]').extract_first() is not None:
                firstBlock = Selector(text=str(sel.xpath('//tr[@class="search_results important first"]').extract_first()))
            #print(str(firstBlock.xpath('//tr[@class="search_results first"]').extract_first()))
            fullForm = getFullForm(firstBlock)
            #print(fullForm)
            allLabels = getLabel(firstBlock)
            #print(allLabels)
            abbrFromHTML = getAbbr(firstBlock)
            #print(abbrFromHTML)
            #s1 = abbrFromHTML + " & " + fullForm + " & " + allLabels
            #print(abbrFromHTML + " & " + fullForm + " & " + allLabels)
            inputRedis.putPair(abbrFromHTML + " & " + fullForm + " & " + allLabels)
            # если поиск вернул более одного сокращения
            if len(sel.xpath('//tr[@class="search_results"]').extract()) > 0:
                for i in range(0, len(sel.xpath('//tr[@class="search_results"]').extract())):
                    #logging.info(str(sel.xpath('//tr[@class="search_results"]').extract()[i]) + "\n")
                    otherBlocks = Selector(text=str(sel.xpath('//tr[@class="search_results"]').extract()[i]))
                    fullForm = getFullForm(otherBlocks)
                    #print(fullForm)
                    allLabels = getLabel(otherBlocks)
                    #print(allLabels)
                    abbrFromHTML = getAbbr(otherBlocks)
                    #print(abbrFromHTML)
                    #s2 = abbrFromHTML + " & " + fullForm + " & " + allLabels
                    #print(abbrFromHTML + " & " + fullForm + " & " + allLabels)
                    inputRedis.putPair(abbrFromHTML + " & " + fullForm + " & " + allLabels)
    logging.info(str(datetime.datetime.now()) + " >>> " + str(inputRedis.abbrBase.dbsize()))
