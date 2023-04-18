def create_allnews_list(news):
    all_news = []
    rounds = len(news)//3 +1
    for i in range(rounds):
        all_news.append(tuple(news[:3]))
        news = news[3:]
    if all_news[-1] == ():
        all_news.pop()
    
    return all_news

def create_home_news(news):
    all_news = []
    rounds = len(news)//2 +1
    for i in range(rounds):
        all_news.append(tuple(news[:2]))
        news = news[2:]
    if all_news[-1] == ():
        all_news.pop()
    return all_news

def create_api_list(api):
    all_api = []
    rounds = len(api)//3 +1
    for i in range(rounds):
        all_api.append(tuple(api[:3]))
        api = api[3:]
    if all_api[-1] == ():
        all_api.pop()
    
    return all_api