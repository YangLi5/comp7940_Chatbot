import requests
import json
import os

#set up headers for news source api
header={'X-Api-Key':os.environ['news_api_key']}

def get_news_from_keyword(keyword):
    news_url = 'https://newsapi.org/v2/everything?language=en&qInTitle='+keyword
    response = requests.get(news_url,headers=header).text
    response = json.loads(response)['articles']

    return_list=[]
    url_list=[]
    for r in response:
        source=r['source']['name']
        author=r['author']
        title=r['title']
        url=r['url']
        url_list.append(str(url))
        return_list.append('\n\nAgency: '+str(source)+'\nAuthor :'+str(author)+'\nTitle: '+title+'\n\nread here: '+str(url))
    
    if len(return_list)>5:
        return url_list,return_list[:5]
    
    return url_list,return_list