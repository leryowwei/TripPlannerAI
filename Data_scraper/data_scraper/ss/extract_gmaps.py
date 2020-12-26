""" This module uses selenium to navigate to google maps to check if the keyword
    is an actual place. If yes, it will extract other useful info and return as a dict.
"""
import re
import time
import math
import random
from urllib.parse import unquote
from .utils import logger
from .constants import GOOGLE_REVIEW_LIMIT
from selenium.webdriver.common.action_chains import ActionChains

def parse_for_info(driver):
    """ Parse for info from google maps website about the location and return 
        all info as a dictionary 
    """
    
    info_dict = {}
    place_name = None

    # (1) try and get place name from url
    try:
        url = driver.current_url
        
        # clean url and unquote url
        # remove https://
        url = unquote(url).replace("https://", "")
        
        # get a list
        url_list = url.split("/")
        
        # list always have google.com, maps, place, PLACE_NAME / google.com, maps, search, PLACE_NAME
        # get place name
        place_name = url_list[3]

        # tidy up place name
        # split to list first using common delimiters
        place_name = re.split("[+ , %20]", place_name)

        # filter list to remove unknown characters and join the list
        place_name = " ".join([letter for letter in place_name if letter not in ["", " "]])
        
    except:
        logger.warning("Failed to get place name from google url {}. No google database is formed..".format(url))
            
    
    # if found place_name continue finding other info
    if place_name:
        # intialise dictionary
        info_dict = {'name': place_name, 'ratings': None, 'address': None,
                     'website': None, 'phone': None, 'price': None, 'plus code': None,
                     'hours':[], 'coordinate':None}
        
        # (2) number of stars
        try:
            x = driver.find_element_by_xpath("//ol[@class='section-star-array']")
            stars = x.get_attribute('aria-label')
            stars = re.findall('[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', stars)[0]
            info_dict['ratings'] = stars
        except:
            pass
    
        # (3-6) address, website, phone number, plus code
        field_list = ['address', 'website', 'phone', 'plus code', 'category']
        
        for x in driver.find_elements_by_xpath("//button"):
            try:
                label = x.get_attribute('aria-label')
                
                if label:
                    for field in field_list:    
                        if "{}: ".format(field) in label.lower():
                            result = label.replace("{}: ".format(field.capitalize()), "")
                            info_dict[field] = result
            except:
                pass
                        
        # (7) price range (only for restaurants)
        for x in driver.find_elements_by_xpath("//span"):
            try:
                label = x.get_attribute('aria-label')
                
                if label:
                    if "Price: " in label:
                        result = label.replace("Price: ", "")
                        info_dict['price'] = result
                        break
            except:
                pass
        
        # (8) category
        for x in driver.find_elements_by_xpath("//button"):
            try:
                label = x.get_attribute('jsaction')
                
                if label:
                    if "category" in label:
                        info_dict['category'] = x.text
                        break
            except:
                pass
        
        # (9) opening hours
        try:
            for x in driver.find_elements_by_xpath("//button[@data-tooltip='Copy open hours']"):
                hours = x.get_attribute('data-value')
                info_dict['hours'].append(hours)
        except:
            pass
    
        # (10) longitude and latitude
        try:
            # use the url list parse previously to get the values - it will be the fourth element
            coord = url_list[4]
            
            # further split 
            coord = re.split("[,]", coord)
            
            # get long and lat
            long = coord[0].replace("@", "")
            lat = coord[1].replace("@", "")
            
            info_dict['coordinate'] = [long, lat]
        except:
            pass
            
    return info_dict

def parse_for_reviews(driver):
    """ Parse for reviews from google maps website about the location and return 
        all info as a dictionary 
    """
    # look for more reviews button and click on it - otherwise means very little reviews
    flag = False
    for button in driver.find_elements_by_xpath("//div[@role='button']"):
        try:
            action = button.get_attribute('jsaction')
            
            if "reviews" in action.lower():
                flag = True
                break
        except:
            pass
        
    # click into reviews and sort the reviews
    if flag:
        try:
            # click and wait
            button.click()
            time.sleep(2)
        except:
            pass

        try:
            # use sorting to make the page dynamic - have to first choose most recent reviews to refresh the page
            # then choose most relevant button again - interested in most relevant
            # click sort button
            sort_bt = driver.find_element_by_xpath("//button[@aria-label='Sort reviews']")
            sort_bt.click()
            time.sleep(1)

            # first element of the list: most recent
            most_recent_bt = driver.find_elements_by_xpath("//li[@role='menuitemradio']")[1]
            most_recent_bt.click()
            time.sleep(1)

            # click sort button
            sort_bt = driver.find_element_by_xpath("//button[@aria-label='Sort reviews']")
            sort_bt.click()
            time.sleep(1)

            # second element of the list: most relevant
            most_relevant_bt = driver.find_elements_by_xpath("//li[@role='menuitemradio']")[0]
            most_relevant_bt.click()
            time.sleep(1)
        except:
            pass

        try:
            # scroll page i times depending on the number of reviews required - assume that one scroll contains 8 reviews
            # this is to load the reviews in advance
            for i in range(0, math.ceil(GOOGLE_REVIEW_LIMIT / 8)):
                scrollable_div = driver.find_element_by_css_selector(
                    'div.section-layout.section-scrollbox.scrollable-y.scrollable-show')
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                # use random waiting time to avoid being spotted as consistent pattern
                time.sleep(round(random.uniform(1, 2), 1))
        except:
            pass

    # start parsing reviews
    reviews_list = []

    # first expand 'more buttons' of review if exists
    for ite, container in enumerate(driver.find_elements_by_xpath("//div[@class='section-review-content']"), 1):
        # check if got more button - click it if exists
        try:
            child_btn = container.find_element_by_xpath("//button[contains(text(), 'More')]")
            child_btn.click()
            driver.implicitly_wait(1)
        except:
            pass

        # exit loop when review quota is reached
        if ite >= GOOGLE_REVIEW_LIMIT:
            break

    # get review text
    for ite, review in enumerate(driver.find_elements_by_xpath("//span[@class='section-review-text']"), 1):
        # write review
        reviews_list.append({'review': review.text, 'ratings': None, 'date': None})

        # exit loop when review quota is reached
        if ite >= GOOGLE_REVIEW_LIMIT:
            break

    # get review ratings
    for ite, rating in enumerate(driver.find_elements_by_xpath("//span[@class='section-review-stars']")):
        # write ratings
        reviews_list[ite]['ratings'] = rating.get_attribute('aria-label')

        # exit loop when review quota is reached
        if ite + 1 >= GOOGLE_REVIEW_LIMIT:
            break

    # get published date
    for ite, date in enumerate(driver.find_elements_by_xpath("//span[@class='section-review-publish-date']")):
        # write published dates
        reviews_list[ite]['date'] = date.text

        # exit loop when review quota is reached
        if ite + 1 >= GOOGLE_REVIEW_LIMIT:
            break

    return reviews_list


def extract_gmaps(keyword, driver):
    """ This function uses selenium to navigate to google maps to check if the keyword
        is an actual place. If not, get google to return the best result.
        
        If no results is found, return empty string.
        
        TODO: improve efficiency of the code... first pass code takes very long.
        One improvement is to improve the wait function to make it explicit wait
    """ 
    # search google maps using the keyword
    gmaps_website ="https://www.google.com/maps/search/{}".format(keyword)
    driver.get(gmaps_website)
    driver.implicitly_wait(1)

    # initialisation
    no_match = None

    # give consent if exists
    try:
        frame_reference = driver.find_element_by_class_name("widget-consent-frame")
        driver.switch_to.frame(frame_reference)
        driver.find_element_by_xpath("//div[@id='introAgreeButton']").click()
        driver.switch_to.default_content()
    except:
        pass
    
    # check if results are found
    # if any keywords in the list are found, means no results
    list_of_keywords = ['Partial match', 'No results found for', "Google Maps can\'t find"]
    
    for phrase in list_of_keywords:
        no_match = driver.find_elements_by_xpath('//*[contains(text(), "{}")]'.format(phrase))
        
        if no_match:
            break
    
    # if got results, continue to find out the location's info
    if not no_match:
        list_flag = False
        
        # if got list of results then turn flag on
        for x in driver.find_elements_by_xpath("//div"):
            try:
                # find out aria-label
                label = x.get_attribute('aria-label')
    
                # normally aria label will be 'Results for haji lane' - then it means got a list of places
                if 'Results for' in label:
                    list_flag = True
            except:
                pass
            
            # exit loop
            if list_flag:
                break
        
        # if is list, navigate to the page of the first result
        if list_flag:
            # find all elements that are button
            div_eles = driver.find_elements_by_xpath("//div[@role='button']") + \
                       driver.find_elements_by_xpath("//a[@role='button']")
            
            for x in div_eles:
                try:
                    # find out aria-label
                    label = x.get_attribute('aria-label')
                    
                    # ignore common words - exit for loop at the first result found
                    if label.lower() not in ['none', 'google maps', 'map', 'clear search', 
                                             'available filters for this search', 'see more', 
                                             'i agree', 'results for {}'.format(keyword)]: 
                        break
                except:
                    pass
            
            # click on the first result found and wait for the webpage to change
            try:
                x.click()
                driver.implicitly_wait(2)
            except:
                pass

        # Start parsing google webpage and get all info
        info_dict = parse_for_info(driver)
        
        # parse for google reviews
        info_dict['reviews'] = parse_for_reviews(driver)
        
    else:
        info_dict = {}
        logger.info('Nothing found on google for {}....'.format(keyword))

    return info_dict

