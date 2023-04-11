# -*- coding: utf-8 -*-
# Author: Feng Pan (fengpan1994@gmail.com)

import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from collections import Counter
import os
import random
import datetime


def get_one_page(url):
    send_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8"}
    response = requests.get(url,headers=send_headers)
    while response.status_code == 403:
        time.sleep(500 + random.uniform(0, 500))
        response = requests.get(url,headers=send_headers)
        print(response.status_code)
    if response.status_code == 200:
        return response.text

    return None

def get_date_today():
    day = datetime.date.today().strftime('%a,  %d %b %y').split(' ')
    if day[2][0] == '0': day[2] = ' ' + day[2][1:]
    day.pop(1)
    return ' '.join(day) 


def main():
    data_collect_failure = False
    t0 = time.time()
    # while not data_collect_failure:
    try:
        domains = ['cond-mat.stat-mech', 'cond-mat.dis-nn', 'quant-ph']
        arxiv_ids = []
        titles = []
        authors = []
        abstracts = []
        domain_failure = [0] * len(domains)
        for domain in domains:
            url = 'https://export.arxiv.org/list/'+domain+'/new'
            html = get_one_page(url)
            soup = BeautifulSoup(html, features='html.parser')
            date = soup.find('h3').text.split(' for ')[1]
            print(date)
            date_today = get_date_today()
            if date != date_today:
                domain_failure[domains.index(domain)] = 1
                print(date_today)
                print(f'No new updates in {domain} today, or maybe try later.')
            sections = [item.text.split(' for ')[0] for item in soup.find_all('h3')]
            all_section = soup.find_all('dl')
            assert len(all_section) == len(sections)
            contents = [all_section[i] for i in range(len(sections)) if sections[i] in ['New submissions', 'Cross-lists']]
            for content in contents:
                arxiv_ids += content.find_all('a', title = 'Abstract')
                titles += content.find_all('div', class_ = 'list-title mathjax')
                authors += content.find_all('div', class_ = 'list-authors')
                abstracts += content.find_all('p', 'mathjax')

        if sum(domain_failure) == len(domains):
            return None

        url_search = 'https://arxiv.org/search/?query=tensor+networks&searchtype=all'
        soup_search = BeautifulSoup(get_one_page(url_search), features='html.parser')
        content_search = soup_search.find('ol')

        arxiv_ids_search = []
        titles_search = []
        authors_search = []
        abstracts_search = []
        arxiv_ids_search += [c.find_all('a')[0] for c in content_search.find_all('p', class_='list-title is-inline-block')] # content_search.find_all('p', class_='list-title is-inline-block')
        titles_search += content_search.find_all('p', class_ = 'title is-5 mathjax')
        authors_search += content_search.find_all('p', class_ = 'authors')
        abstracts_search += content_search.find_all('span', class_='abstract-full has-text-grey-dark mathjax')
        data_collect_failure = True
    except:
        time.sleep(3)
        if time.time() - t0 > 500:
            raise TimeoutError("Waiting too long for connectin response.")


    name = ['id', 'url', 'title', 'author', 'abstract']
    archived_search_results_path = './paper/'
    archived_search_results_file = archived_search_results_path + 'search_archived.csv'
    if os.path.exists(archived_search_results_file):
        archived_search_results = pd.read_csv(archived_search_results_file)
    else:
        if not os.path.exists(archived_search_results_path):
            os.mkdir(archived_search_results_path)
        archived_search_results = pd.DataFrame(columns=name, data=[])
    
    items = []
    assert len(arxiv_ids) == len(titles) == len(abstracts) == len(authors)
    for i in range(len(arxiv_ids)):
        items.append(
            [
                arxiv_ids[i].text,
                'https://arxiv.org/abs/'+arxiv_ids[i].text[6:],
                titles[i].text.replace('\nTitle: ', '').strip('\n'), 
                ''.join(authors[i].text.split('\n')[2:]),
                ' '.join(abstracts[i].text.split('\n'))
            ]
        )
    search_items = []
    assert len(arxiv_ids_search) == len(titles_search) == len(abstracts_search) == len(authors_search)
    for i in range(len(arxiv_ids_search)):
        data = [
            arxiv_ids_search[i].text,
            'https://arxiv.org/abs/'+arxiv_ids_search[i].text[6:],
            titles_search[i].text.split('\n')[2].strip(' '),
            ''.join([string.lstrip(' ') for string in authors_search[i].text.strip('\nAuthors:\n').split('\n')]),
            abstracts_search[i].text.split('\n')[1].strip(' ')
        ]
        if arxiv_ids_search[i].text not in list(archived_search_results.id):
            items.append(data)
        search_items.append(data)
    
    papers_search = pd.DataFrame(columns=name, data=search_items)
    papers_search.to_csv(archived_search_results_file)

    papers = pd.DataFrame(columns=name, data=items)
    papers = papers.drop_duplicates(subset='id', keep='first')
    f = open('paper/'+time.strftime("%Y-%m-%d")+'.txt', 'w')
    for p in papers.iloc:
        paper_data = list(p)
        for data in paper_data:
            f.write(data + '\n')
        f.write('\n')
    f.close()
    # papers.to_csv('paper/'+time.strftime("%Y-%m-%d")+'_'+str(len(items))+'.csv')


if __name__ == '__main__':
    main()