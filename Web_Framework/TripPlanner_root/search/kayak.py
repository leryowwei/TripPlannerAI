# base class for kayak scraper

import datetime
import time
import math
from selenium import webdriver


class Kayak:
    def __init__(self, headless):
        """Build kayak scraper base class and contain methods that can be shared with child classes"""

        # set up webdriver object
        webdriver_path = "D:/Documents/GitHub/TripPlannerAI/Miscellaneous/chromedriver_win32/chromedriver.exe"
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        try:
            option = webdriver.ChromeOptions()
            option.add_argument('window-size=1920x1080')
            option.add_argument("--start-maximized")
            option.add_argument(f'user-agent={user_agent}')
            if headless:
                # make headless undetectable https://intoli.com/blog/making-chrome-headless-undetectable/
                option.add_argument('headless')
            self.driver = webdriver.Chrome(executable_path=webdriver_path, options=option)
        except:
            raise ValueError("Failed in setting up webdriver. Please check if webdriver is in Miscellaneous folder.")

        # assign base url
        self.base_url = 'https://www.kayak.co.uk'

    def _give_consent(self):
        """Give consent to website"""
        # try and see if consent window exists and accept it
        # got different types of accept all cookies so this is backup plan
        try:
            self.driver.find_element_by_xpath("//button[@aria-label='Accept']").click()
        except:
            try:
                self.driver.find_element_by_xpath("//button[contains(text(), 'Accept All Cookies')]").click()
            except:
                pass

    @staticmethod
    def _validate_date(date_text):
        """Check if date is correct

            TODO: currently assume we only allow exact date to simplify algorithm. In reality, we can define YYYY-MM or
            anytime. Also assume that all dates need to be specified and cannot be empty
        """
        # allowable formats are YYYY-MM-DD
        if date_text:
            try:
                datetime.datetime.strptime(date_text, '%Y-%m-%d')
            except ValueError:
                raise ValueError("Incorrect data format, should be YYYY-MM-DD")
        else:
            raise ValueError("Inbound and outbound dates cannot be empty.")

    @staticmethod
    def _convert_db_row_to_dict(db_info, colnames):
        """Convert a single row from sql database to dictionary"""
        tmp_dict = {}
        if db_info:
            for ite, col in enumerate(colnames):
                tmp_dict[col[0]] = db_info[ite]
        return tmp_dict

    @staticmethod
    def _convert_dict_to_db_cmd(tmp_dict, colnames):
        """Convert dictionary to a row of values to write back to sql"""
        x = ""
        for col in colnames:
            x += "'{}',".format(tmp_dict[col[0]])
        print(x)
        return x

    def load_wbdriver(self, url):
        """Load webdriver object based on url provided"""

        # load driver to the website and give consent
        self.driver.get(url)
        time.sleep(5)
        self._give_consent()
        time.sleep(10)

    def show_more_results(self, no_of_results, results_per_page):
        """Click the show more results button depending on how many results we are interested in"""

        # work out how many times the show more results button needs to be pressed
        no_of_times = math.ceil(no_of_results / results_per_page) - 1

        # start pressing
        for ite in range(0, no_of_times):
            # check if show more results button exists, if exists, then click
            # otherwise exit loop
            try:
                self.driver.find_element_by_css_selector("div[class='resultsListFooter clearfix']"). \
                    find_element_by_css_selector("a[class='moreButton']").click()
                time.sleep(5)
            except:
                break

        # scroll to top of page
        self.driver.execute_script("window.scroll(0, 0);")
