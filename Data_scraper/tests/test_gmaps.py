import os
import sys
sys.path.append('../')
from selenium import webdriver
from data_scraper.extract_gmaps import extract_gmaps

# set up relevant paths
parent_path = os.path.abspath('../..')
webdriver_path = os.path.join(parent_path, 'Miscellaneous', 'chromedriver_win32', 'chromedriver.exe')
misc_path = os.path.join(parent_path, 'Miscellaneous')

option = webdriver.ChromeOptions()          
#option.add_argument('headless')
option.add_argument('window-size=1920x1080')

option.add_argument("--log-level=3")
driver = webdriver.Chrome(executable_path = webdriver_path, options = option)

keyword = "marina bay sands singapore singapore"

extract_gmaps(keyword, driver)

