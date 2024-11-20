import os
import sys
import time
import random
import string

from .variables import (
    bing_config,
    info,
    error
)
from .utils import cache
import requests
from requests.exceptions import HTTPError
import pandas as pd

LINKS_TO_EXCLUDE = ["-site:youtube.com", "-site:twitter.com", "-site:facebook.com", "-site:klinikhoaks.jatimprov.go.id", "-site:saberhoaks.jabarprov.go.id", "-site:opendata.jabarprov.go.id"]

class RateLimitError(Exception):
    pass

class BingInstance:
    def __init__(self):
        global cache_size

        self.api_key = bing_config['api_key']
        if not bing_config['api_key']:
            env_key = os.environ.get('BING_KEY', None)
            self.api_key = env_key
        assert self.api_key is not None, 'No Bing API Key provided!'
        self.search_url = bing_config['endpoint']
        self.cache_file = bing_config['cache_file']
        self.wait_time = bing_config['wait_time']
        self.max_retry = bing_config['max_retry']

    @cache(cache_type = 'bing_search')
    def fetch_bing(self, query, startdate, enddate, tags, kata_kunci):
        
        tags = tags.strip().lstrip().rstrip()
        kata_kunci = kata_kunci.strip().lstrip().rstrip()
        
        # preprocessed the keyword search
        tags_split = ','.join([str(t).strip().lstrip().rstrip() for t in tags.split(",")])
        kata_kunci_split = ','.join([str(t).strip().lstrip().rstrip() for t in kata_kunci.split(",")])
        
        # add query parameter with link to exclude and keywords / tags
        query = query + " AND (" + tags_split + ")" + " AND (" + kata_kunci_split + ")" + " " + " ".join(LINKS_TO_EXCLUDE)
        
        headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        #params = {'q':query, 'mkt': 'en-ID', 'freshness': startdate + '..' + enddate, 'responseFilter': 'News,Webpages'}
        params = {'q':query, 'mkt': 'en-ID'}

        count = 0
        relevant_results = []
        while count < self.max_retry:
            count += 1
            try:
                response = requests.get(self.search_url, headers=headers, params=params)
                response.raise_for_status()
                search_results = response.json()
                
                print("search_results:", search_results)
                sys.stdout.flush()
            
                if 'webPages' not in search_results: # bing api如果调用太频繁，会拒绝相应
                    error(f'call bing api failed, retry after {self.wait_time} seconds...')
                    time.sleep(self.wait_time)
                    continue
                else:
                    # Filter results based on relevance score (adjust the threshold as needed)
                    #relevant_results = [result for result in search_results.get("webPages", {}).get("value", []) if result.get("score", 0) >= 0.7]
                    # Now relevant_results contains only the relevant resultsscrape_news_concurren
                    return search_results
                    #return relevant_results

            except Exception as e:
                raise e
                
    @cache(cache_type = 'bing_search')
    def fetch_bing_with_retry(self, query, startdate, enddate, tags, kata_kunci, max_retry=10):
        
        
        if (tags is None) and (kata_kunci is None):
            # add query parameter with link to exclude and keywords / tags
            query = query + " " + " ".join(LINKS_TO_EXCLUDE) # this excluded list causes zero web return
            
            #query = query 

            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            params = {'q':query, 'mkt': 'en-ID'}

            count = 0
            relevant_results = []
            while (count < self.max_retry) or (count < max_retry):
                count += 1
                try:
                    response = requests.get(self.search_url, headers=headers, params=params)
                    response.raise_for_status()
                    search_results = response.json()
                    print("search_results:", search_results)
                    sys.stdout.flush()
                    return search_results
                except RateLimitError as e:  # Replace RateLimitError with the actual exception
                    count += 1
                    wait_time = 2 ** retry_count + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Rate limit exceeded. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                except HTTPError as e:
                    if e.response.status_code == 429:
                        print("Rate limit exceeded")
                    else:
                        print("An HTTP error occurred")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
            print("Max retries exceeded. Unable to fetch data.")
            return None
        elif (tags is None) and (len(str(kata_kunci))!=0):
            kata_kunci = kata_kunci.strip().lstrip().rstrip()

            # add query parameter with link to exclude and keywords / tags
            query = query + " AND (" + kata_kunci + ")" + " " + " ".join(LINKS_TO_EXCLUDE)
            #query = query + " " + "AND (" + tags + ")" + " AND (" + kata_kunci + ")"

            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            #params = {'q':query, 'mkt': 'en-ID', 'freshness': startdate + '..' + enddate, 'responseFilter': 'News,Webpages'}
            params = {'q':query, 'mkt': 'en-ID'}

            count = 0
            relevant_results = []
            while (count < self.max_retry) or (count < max_retry):
                count += 1
                try:
                    response = requests.get(self.search_url, headers=headers, params=params)
                    response.raise_for_status()
                    search_results = response.json()
                    print("search_results:", search_results)
                    sys.stdout.flush()
                    return search_results
                except RateLimitError as e:  # Replace RateLimitError with the actual exception
                    count += 1
                    wait_time = 2 ** retry_count + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Rate limit exceeded. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                except HTTPError as e:
                    if e.response.status_code == 429:
                        print("Rate limit exceeded")
                    else:
                        print("An HTTP error occurred")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
            print("Max retries exceeded. Unable to fetch data.")
            return None
        else:
            tags = tags.strip().lstrip().rstrip()
            kata_kunci = kata_kunci.strip().lstrip().rstrip()

            # add query parameter with link to exclude and keywords / tags
            query = query + " " + "AND (" + tags + ")" + " AND (" + kata_kunci + ")" + " " + " ".join(LINKS_TO_EXCLUDE)
            #query = query + " " + "AND (" + tags + ")" + " AND (" + kata_kunci + ")"

            headers = {'Ocp-Apim-Subscription-Key': self.api_key}
            #params = {'q':query, 'mkt': 'en-ID', 'freshness': startdate + '..' + enddate, 'responseFilter': 'News,Webpages'}
            params = {'q':query, 'mkt': 'en-ID'}

            count = 0
            relevant_results = []
            while (count < self.max_retry) or (count < max_retry):
                count += 1
                try:
                    response = requests.get(self.search_url, headers=headers, params=params)
                    response.raise_for_status()
                    search_results = response.json()
                    print("search_results:", search_results)
                    sys.stdout.flush()
                    return search_results
                except RateLimitError as e:  # Replace RateLimitError with the actual exception
                    count += 1
                    wait_time = 2 ** retry_count + random.uniform(0, 1)  # Exponential backoff with jitter
                    print(f"Rate limit exceeded. Retrying in {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                except HTTPError as e:
                    if e.response.status_code == 429:
                        print("Rate limit exceeded")
                    else:
                        print("An HTTP error occurred")
                except Exception as e:
                    print(f"An error occurred: {e}")
                    break
            print("Max retries exceeded. Unable to fetch data.")
            return None
               


    def filter_website(self, websites):
        pass

    def postprocess_news_response(self, search_results):
        
        print("search_results:", search_results)
        sys.stdout.flush()
        
        print("search_results keys:", search_results.keys())
        sys.stdout.flush()
        
        required_columns = ['name', 'url', 'description']
        filtered_results = pd.DataFrame(search_results['value'])[required_columns]

        filtered_results = filtered_results.rename(columns={'description':'snippet', 'name':'title'}) # 统一格式

        return filtered_results

    def postprocess_response(self, search_results):
        
        # add none condition        
        if search_results is None:
            print("No results returned.")
            return pd.DataFrame()  # Return an empty DataFrame or handle as needed

        web_pages = search_results.get('webPages', {})
        value = web_pages.get('value', [])
        
        if not value:
            print("No web pages found in the response.")
            return pd.DataFrame()  # Return an empty DataFrame or handle as needed
    
        required_columns = ['name', 'snippet', 'url']
        try:
            print("len search_results['webPages']['value']:", len(search_results['webPages']['value']))
            sys.stdout.flush()
            filtered_results = pd.DataFrame(search_results['webPages']['value'])[required_columns]
            filtered_results = filtered_results.rename(columns={'name': 'title'})  # 统一格式
        except KeyError as e:
            print(f"Missing expected columns: {e}")
            filtered_results = pd.DataFrame()  # Return an empty DataFrame or handle as needed
        except Exception as e:
            print(f"An error occurred while processing results: {e}")
            filtered_results = pd.DataFrame()  # Return an empty DataFrame or handle as needed
            
        return filtered_results




