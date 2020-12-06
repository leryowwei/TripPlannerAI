""" This module uses selenium to navigate to google maps to check if the keyword
    is an actual place.
"""
import re

def extract_gmaps(keyword, driver):
    """ This function uses selenium to navigate to google maps to check if the keyword
        is an actual place. If not, get google to return the best result.
        
        If no results is found, return empty string.
        
        TODO: improve efficiency of the code... first pass code takes very long.
        One improvement is to improve the wait function to make it explicit wait
    """ 
    gmaps_website ="https://www.google.com/maps/search/{}".format(keyword)
    driver.get(gmaps_website)
    driver.implicitly_wait(5)
    
    place = None
    
    # check if results are found
    # if any keywords in the list are found, means no results
    list_of_keywords = ['Partial match', 'No results found for', "Google Maps can\'t find"]
    
    for phrase in list_of_keywords:
        no_match = driver.find_elements_by_xpath('//*[contains(text(), "{}")]'.format(phrase))
        
        if no_match:
            break
    
    # if got results, continue to find out the place name
    if not no_match:
        xx = driver.find_elements_by_xpath("//div")
        
        list_flag = False
        
        # if got list of results then turn flag on
        for x in xx:
            try:
                # find out aria-label
                label = x.get_attribute('aria-label')
    
                #normally aria label will be 'Results for haji lane' - then it means got a list of places
                if 'Results for' in label:
                    list_flag = True
            except:
                pass
            
            # exit loop
            if list_flag:
                break
        
        # if is list, take the first result
        # otherwise, take the current url       
        if list_flag:
            for x in xx:
                try:
                    # find out aria-label and button
                    label = x.get_attribute('aria-label')
                    role = x.get_attribute('role')
                    
                    # ignore common words and with button
                    if label.lower() not in ['none', 'google maps', 'map', 'available filters for this search', 'results for {}'.format(keyword)] and role == 'button':
                        place = label
                        break
                except:
                    pass
        else:
            url = driver.current_url
            
            # clean url
            # remove https://
            url = url.replace("https://", "")
            # get a list
            url_list = url.split("/")
            
            # list always have google.com, maps, place, PLACE_NAME / google.com, maps, search, PLACE_NAME
            # get place name
            place = url_list[3]
            
            # tidy up place name
            # split to list first using common delimiters
            place = re.split("[+ , %20]", place)
            
            # filter list to remove unknown characters and join the list
            place = " ".join([letter for letter in place if letter not in ["", " "]])
            
        print ("{} found on google for keyword: {}".format(place, keyword))          
    else:
        print ('Nothing found on google for {}....'.format(keyword))

    return place