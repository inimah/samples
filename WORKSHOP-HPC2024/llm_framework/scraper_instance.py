# 爬取指定url的新闻文章内容
import os
import sys

import concurrent.futures
from .variables import (
    scraper_config,
    info,
    web_proxy,
    error
)
from .utils import cache
from newspaper import Article, Config
import time
from trafilatura import bare_extraction

class WebScraper:
    def __init__(self):
        self.max_retry = scraper_config['max_retry']
        self.num_threads = scraper_config['num_threads']
        self.cache_file = scraper_config['cache_file']
        self.document_num = scraper_config['document_num']

    def trafilatura_extract(self, html_doc):
        extracted_doc = bare_extraction(html_doc)

        if extracted_doc == None:
            return ''
        else:
            return f'{extracted_doc["description"]} {extracted_doc["text"]}'


    
    #def scrape_news(self, url):
    @cache(cache_type='newspaper')
    def scrape_news(self, url):
       
        html_doc = None
               
        print("url from Bing:", url)
        sys.stdout.flush()
        
        config = Config()
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
        #user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko'
        config.fetch_images = False #True
        #config.request_timeout = 10
        config.browser_user_agent = user_agent
        config.keep_article_html = True
        config.memoize_articles = False
        
        for _ in range(self.max_retry):
            try:
                
                #article = Article(url, proxies=web_proxy)
                article = Article(url, config=config)
                article.download()
                # parsing article
                article.parse()
                # nlp function
                #article.nlp()
                if article.html is None:
                    info(f'url:{url} fetch error, retry after 50 second')
                    time.sleep(5) # wait time 50s
                    continue
                else:
                    html_doc = article.html
                    article.parse()
                    time.sleep(5)
                    break

            except Exception as e:
                error(f'url:{url} fetch error, retry after 10 second')
                time.sleep(5)

        if html_doc is None:
            # this may due to HTTP client error: 401, dst
            # use the title and snipper from BING results instead
            '''
            print("article.text:", article.text)
            sys.stdout.flush()
            print("article.keywords:", article.keywords)
            sys.stdout.flush()
            print("article.summary:", article.summary)
            sys.stdout.flush()
            '''
            
            error(f'url:{url} fetch failed')
            return ''
        else:
            
            #print("html_doc before being scraped:", html_doc)
            #sys.stdout.flush()
            
            # put exception here because the scrapper cannot handle malformed web
            trafilatura_extract_doc = None
            newspaper_extracted_doc = article.text.strip()
            
            try:
                trafilatura_extract_doc = self.trafilatura_extract(html_doc).strip()
                
                if trafilatura_extract_doc is None:
                    return ""
                
            except Exception as e:
                error(f'Exception during extraction: {e}')
                return ""
            if trafilatura_extract_doc != '':
                return trafilatura_extract_doc
            else:
                return newspaper_extracted_doc # 这个也可能为空

    def scrape_news_concurrent(self, results_df):
        
        if results_df.empty:
            print('DataFrame is empty!')
            print("No web pages found in the response.")
        else:
            print("Bing results_df:", results_df)
            sys.stdout.flush()

            title = results_df['title']
            snippet = results_df['snippet']
            merged_snippet = title + ". " + snippet

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
                batch_results = list(executor.map(self.scrape_news, results_df['url']))
                #batch_results = list(executor.map(self.scrape_news, results_df['url'], merged_snippet))
            results_df.loc[:, 'document'] = batch_results
            # filtered_results = list(filter(lambda x: x is not None and x.strip() != '', batch_results)) # 过滤掉空字符串和None
            # return filtered_results[:self.document_num]

