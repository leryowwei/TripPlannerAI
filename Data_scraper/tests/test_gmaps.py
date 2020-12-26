""" Testing module for google maps and trip advisor modules """
import os
import sys
sys.path.append('../')
from selenium import webdriver
from data_scraper.extract_gmaps import extract_gmaps
import data_scraper.constants as constants
from data_scraper.user import User
from data_scraper.gmaps import GoogleMapsLocationInfo, GoogleMapsLocationReview

# set up relevant pathssssss
parent_path = os.path.abspath('../..')
webdriver_path = os.path.join(parent_path, 'Miscellaneous', 'chromedriver_win32', 'chromedriver.exe')
misc_path = os.path.join(parent_path, 'Miscellaneous')

option = webdriver.ChromeOptions()
#option.add_argument('headless')
option.add_argument('window-size=1920x1080')

option.add_argument("--log-level=3")
driver = webdriver.Chrome(executable_path = webdriver_path, options = option)

# setup user class
user_class = User(constants.DEFAULT_USER)

keyword = "hawker centre Singapore"

gmaps_info = GoogleMapsLocationInfo(driver, keyword)

print(gmaps_info.place_name)

if 'singapore' in gmaps_info.get_address().lower():
    loc_info = gmaps_info.build_loc_database()

    print(loc_info)

    gmaps_review = GoogleMapsLocationReview(driver, gmaps_info.url, gmaps_info.place_name)
    loc_reviews = gmaps_review.build_loc_reviews()

    for ite, review in enumerate(loc_reviews, 1):
        print("--{}----------------------------".format(ite))
        print(review)

    driver.quit()