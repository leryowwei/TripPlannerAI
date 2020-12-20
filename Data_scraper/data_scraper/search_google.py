from googlesearch import search 

def define_googlequery(user_class):
    """ Form a list of queries to search google """
    
    # unwrap class attributes
    place = user_class.place
    # country = user_class.country

    # TODO: need to work out algorithms to define a highly customised list
    query_list = [place + " timeout to do list",
                   place + " where to eat eater",
                   place + " romantic things to do",
                   place + " itinerary 3 days",
                   place + " places to eat local",
                   place + " adventurous activities",
                   place + " nature things to do",
                   place + " nature spots",
                   place + " parks",
                   place + " relaxing things to do",
                   place + " relaxing spots",
                   place + " cultural attractions",
                   place + " museums",
                   place + " historical sites",
                   place + " hidden gems",
                   place + " best restaurants 2020",
                   place + " must eat where",
                   place + " hawker centre",
                   place + " romantic restaurants",
                   place + " michelin restaurants timeout",
                   place + " best cheap eats",
                   place + " best bars",
                   place + " must visit bars",
                   place + " nightlife",
                   place + " shopping",
                   place + " where to shop",
                   place + " must see places",
                   place + " adventure ideas",
                 ]

    return query_list 

def request_urls(query_list, user_class, num_result=1, pause_time=1):
    """ Takes in the user's search keywords and finds out the relevant urls
    """ 
    # google search to get urls
    search_urls = []
    for query in query_list:
        search_urls.extend(search(query, stop=num_result, pause=pause_time, 
                                  country=user_class.country))
    
    return search_urls