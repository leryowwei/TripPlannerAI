""" This module extracts information from trip advisor for a particular location 
    using selenium.

    Information extracted are:
        (1) Tripadvisor webpage
        (2) Suggested duration
        (3) tripadvisor reviews
"""
import requests
import webbrowser
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By

def display(content, filename='output.html'):
    with open(filename, 'wb') as f:
        f.write(content)
        webbrowser.open(filename)

def get_soup(session, url, show=False):
    r = session.get(url)
    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[get_soup] status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')

def post_soup(session, url, params, show=False):
    '''Read HTML from server and convert to Soup'''

    r = session.post(url, data=params)

    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[post_soup] status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')

def scrape(url, review_limit, lang='ALL'):

    # create session to keep all cookies (etc.) between requests
    session = requests.Session()

    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
    })


    items = parse(session, review_limit, url + '?filterLang=' + lang)

    return items

def parse(session, review_limit, url):
    '''Get number of reviews and start getting subpages with reviews'''

    soup = get_soup(session, url)

    if not soup:
        print('[parse] no soup:', url)
        return

    url_template = url.replace('-Reviews-', '-Reviews-or{}-')

    items = []

    offset = 5

    while(True):
        subpage_url = url_template.format(offset)

        subpage_items = parse_reviews(session, subpage_url)
        if not subpage_items:
            break

        items += subpage_items

        if len(subpage_items) < 5:
            break

        if offset >= review_limit:
            break

        offset += 5

    return items

def get_reviews_ids(soup):

    items = soup.find_all('div', attrs={'data-reviewid': True})

    if items:
        reviews_ids = [x.attrs['data-reviewid'] for x in items][::]
        return reviews_ids

def get_more(session, reviews_ids):

    url = 'https://www.tripadvisor.com/OverlayWidgetAjax?Mode=EXPANDED_HOTEL_REVIEWS_RESP&metaReferer=Hotel_Review'

    payload = {'reviews': ','.join(reviews_ids)} # ie. "577882734,577547902,577300887"

    soup = post_soup(session, url, payload)

    return soup

def parse_reviews(session, url):
    '''Get all reviews from one page'''

    soup =  get_soup(session, url)

    if not soup:
        print('[parse_reviews] no soup:', url)
        return

    reviews_ids = get_reviews_ids(soup)
    if not reviews_ids:
        return

    soup = get_more(session, reviews_ids)

    if not soup:
        print('[parse_reviews] no soup:', url)
        return

    items = []

    for idx, review in enumerate(soup.find_all('div', class_='reviewSelector')):

        bubble_rating = review.select_one('span.ui_bubble_rating')['class']
        bubble_rating = bubble_rating[1].split('_')[-1]

        item = {'rating': bubble_rating,
                'review': review.find('p', class_='partial_entry').text,
                'date': review.find('span', class_='ratingDate')['title']}

        items.append(item)

    return items
        
def extract_ta_data(keyword, user_class, driver):
    """ main function to extract trip advisor reviews and suggested duration"""

    lang = 'en'
    review_limit = 500
    reviews = {}
    hours = "N/A"
    url = "N/A"

    # add country to keyword
    keyword = "{} {}".format(keyword, user_class.country)

    driver.get("https://www.tripadvisor.co.uk/Attractions-g186220-Activities-Bristol_England.html")

    # put everything in a big try, except loop
    try:
        # find element for search box
        inputElement = driver.find_element_by_css_selector("input[type='search']")

        # type in the search - using keyword
        inputElement.send_keys(keyword)
        inputElement.send_keys(Keys.ENTER)

        # get element after explicitly waiting for 10 seconds 
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "result-title"))) 

        # click the element  
        element.click()  

        driver.implicitly_wait(5)

        driver.switch_to.window(driver.window_handles[-1])

        url = driver.current_url
      
        print ("    Scraping TA data from {}".format(url))

        # try and see if there's suggested duration
        try:
            x = driver.find_element_by_xpath("//span[contains(text(), 'Suggested Duration:')]")
            parent = x.find_element_by_xpath('..')
            
            hours = parent.text.replace("Suggested Duration:", "")
        except:
            pass

        print ("    Suggested duration for this location: %s" % format(hours))

        # get all reviews for 'url' and 'lang'
        reviews = scrape(url, review_limit, lang)
    except:
        print ("    Unable to extract Trip Advisor data for {}".format(keyword))

    # tidy everything together as a dictionary
    tripadvisor_dict = {'reviews': reviews,
                        'hours': hours,
                        'url': url}

    return tripadvisor_dict
