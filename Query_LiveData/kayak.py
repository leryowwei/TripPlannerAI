# base class for kayak scraper

import datetime
import time
import math
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class Kayak:
    def __init__(self, wbdriver):
        """Build kayak scraper base class and contain methods that can be shared with child classes"""
        # assign values first
        self.driver = wbdriver
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
                self.driver.find_element_by_css_selector("div[class='resultsListFooter clearfix']").\
                    find_element_by_css_selector("a[class='moreButton']").click()
                time.sleep(5)
            except NoSuchElementException:
                print("failed")
                break

        # scroll to top of page
        self.driver.execute_script("window.scroll(0, 0);")