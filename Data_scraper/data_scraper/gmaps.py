"""
Python class to build database of a location by using google maps
"""

import re
import time
import math
import random
from urllib.parse import unquote
from .utils import logger
from .constants import GOOGLE_REVIEW_LIMIT


class GoogleMapsLocationInfo:
    def __init__(self, driver, search_term):
        """Build google maps scraper class"""
        # assign to self and initiate variables first
        self.driver = driver
        self.search_term = search_term
        self.place_name = None
        self.url = None

        # search for suggestion and populate place_name
        self._search()

        # populate url
        self.url = self.driver.current_url

    def _give_consent(self):
        """Give consent to google maps website"""
        # try and see if consent window exists and accept it
        try:
            frame_reference = self.driver.find_element_by_class_name("widget-consent-frame")
            self.driver.switch_to.frame(frame_reference)
            self.driver.find_element_by_xpath("//div[@id='introAgreeButton']").click()
            self.driver.switch_to.default_content()
        except:
            pass

    def _no_match(self):
        """ check google maps to see if results are found """
        # if any keywords in the list are found, means no results
        list_of_keywords = ['Partial match', 'No results found for', "Google Maps can\'t find"]
        no_match = None

        for phrase in list_of_keywords:
            no_match = self.driver.find_elements_by_xpath('//*[contains(text(), "{}")]'.format(phrase))

            if no_match:
                break

        return True if no_match else False

    def _is_list(self):
        """Check if google maps results returned are in a list"""
        # if got list of results then turn flag on
        list_flag = False

        for x in self.driver.find_elements_by_xpath("//div"):
            try:
                # find out aria-label
                label = x.get_attribute('aria-label')
                # normally aria label will be 'Results for haji lane' - then it means got a list of places
                if 'Results for' in label:
                    list_flag = True
                    break
            except:
                pass

        return list_flag

    def _click_list_item(self):
        """Choose the first item in the list"""

        # find all elements that are buttons
        div_eles = self.driver.find_elements_by_xpath("//div[@role='button']") + self.driver.find_elements_by_xpath("//a[@role='button']")

        button = None

        for button in div_eles:
            try:
                # find out aria-label
                label = button.get_attribute('aria-label')

                # ignore common words - exit for loop at the first result found
                if label.lower() not in ['none', 'google maps', 'map', 'clear search',
                                         'available filters for this search', 'see more',
                                         'i agree', 'results for {}'.format(self.search_term)]:
                    break
            except:
                pass

        # click on the first result found and wait for the webpage to change
        try:
            button.click()
            self.driver.implicitly_wait(2)
        except:
            pass

    def _search(self):
        """Get googlemaps result based on search term provided"""
        # search google maps using the keyword
        gmaps_website = "https://www.google.com/maps/search/{}".format(self.search_term)
        self.driver.get(gmaps_website)
        time.sleep(2)

        # give consent
        self._give_consent()
        time.sleep(1)

        # if results are found, continue to return a place name, otherwise it is empty
        if not self._no_match():
            # if more than one result is returned, need to choose the first result
            if self._is_list():
                self._click_list_item()
                time.sleep(2)

            # get place name
            self.place_name = self.get_place_name()
        else:
            self.place_name = None

    def _get_url_list(self):
        """clean current url of driver and convert it to a list"""
        # clean url and unquote url
        # remove https://
        url = unquote(self.driver.current_url).replace("https://", "")

        # get a list
        return url.split("/")

    def _get_aria_label(self, header, aria_label):
        """Get result for an aria-label name for a particular header type"""
        result = None

        for x in self.driver.find_elements_by_xpath("//{}".format(header)):
            try:
                label = x.get_attribute('aria-label')

                if label:
                    if "{}: ".format(aria_label) in label.lower():
                        result = label.replace("{}: ".format(aria_label.capitalize()), "")
            except:
                pass

        return result

    def get_place_name(self):
        """Get place name from url"""
        try:
            # get place name from url which is converted to list
            place_name = self._get_url_list()[3]

            # tidy up place name
            # split to list first using common delimiters
            place_name = re.split("[+ , %20]", place_name)

            # filter list to remove unknown characters and join the list
            return " ".join([letter for letter in place_name if letter not in ["", " "]])
        except:
            logger.warning(
                "Failed to get place name from google url {}. No google database is formed..".format(self.driver.current_url))
            return None

    def get_coordinates(self):
        """Get longitudinal and latitude of the location"""
        try:
            # use the url list to get the values - it will be the fourth element
            coord = self._get_url_list()[4]

            # further split
            coord = re.split("[,]", coord)

            # get long and lat
            long = coord[0].replace("@", "")
            lat = coord[1].replace("@", "")

            return [long, lat]
        except:
            return None

    def get_category(self):
        """Get category of the location"""
        category = None

        for x in self.driver.find_elements_by_xpath("//button"):
            try:
                label = x.get_attribute('jsaction')

                if label:
                    if "category" in label:
                        category = x.text
            except:
                pass

        return category

    def get_overall_ratings(self):
        """ Get overall ratings"""
        try:
            x = self.driver.find_element_by_xpath("//ol[@class='section-star-array']")
            stars = x.get_attribute('aria-label')
            stars = re.findall('[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', stars)[0]
            return stars
        except:
            return None

    def get_opening_hours(self):
        """ Get opening hours """
        hours = []
        try:
            for x in self.driver.find_elements_by_xpath("//button[@data-tooltip='Copy open hours']"):
                hours.append(x.get_attribute('data-value'))
        except:
            pass
        return hours

    def get_price_range(self):
        """ Get price range (only for restaurants """
        return self._get_aria_label('span', 'price')

    def get_address(self):
        """ Get address """
        return self._get_aria_label('button', 'address')

    def get_plus_code(self):
        """ Get plus code """
        return self._get_aria_label('button', 'plus code')

    def get_phone_number(self):
        """ Get phone number """
        return self._get_aria_label('button', 'phone number')

    def get_website(self):
        """ Get website """
        return self._get_aria_label('button', 'website')

    def build_loc_database(self):
        """Build database of the location found and return as a dictionary"""
        if self.place_name:
            logger.info('    Building google database...')
            loc_dict = {'name': self.place_name,
                        'coordinates': self.get_coordinates(),
                        'ratings': self.get_overall_ratings(),
                        'address': self.get_address(),
                        'website': self.get_website(),
                        'phone_number': self.get_phone_number(),
                        'price': self.get_price_range(),
                        'plus_code': self.get_plus_code(),
                        'hours': self.get_opening_hours(),
                        'category': self.get_category()}
        else:
            loc_dict = {}

        return loc_dict


class GoogleMapsLocationReview:
    def __init__(self, driver, url, place_name):
        """Build google maps scraper class"""
        # assign driver
        self.driver = driver
        self.url = url
        self.place_name = place_name

        # load driver to the website and give consent
        self.driver.get(self.url)
        time.sleep(2)
        self._give_consent()

    def _give_consent(self):
        """Give consent to google maps website"""
        # try and see if consent window exists and accept it
        try:
            frame_reference = self.driver.find_element_by_class_name("widget-consent-frame")
            self.driver.switch_to.frame(frame_reference)
            self.driver.find_element_by_xpath("//div[@id='introAgreeButton']").click()
            self.driver.switch_to.default_content()
        except:
            pass

    def _load_reviews_page(self):
        """Load reviews page from google maps"""
        flag = False
        button = None

        for button in self.driver.find_elements_by_xpath("//div[@role='button']"):
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

    def _scroll(self):
        """ Scroll page i times depending on the number of reviews required to be scraped"""
        try:
            # scroll page i times depending on the number of reviews required - assume that one scroll contains 2 reviews
            # this is to load the reviews in advance
            for i in range(0, math.ceil(GOOGLE_REVIEW_LIMIT / 2)):
                scrollable_div = self.driver.find_element_by_css_selector(
                    'div.section-layout.section-scrollbox.scrollable-y.scrollable-show')
                self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                # use random waiting time to avoid being spotted as consistent pattern
                time.sleep(round(random.uniform(0.5, 1.5), 1))
        except:
            pass

    def _expand_reviews(self):
        """Expand reviews if a 'more' button exists"""
        # expand 'more buttons' of review if exists
        for ite, container in enumerate(self.driver.find_elements_by_xpath("//div[@class='section-review-content']"), 1):
            # check if got more button - click it if exists
            try:
                child_btn = container.find_element_by_xpath("//button[contains(text(), 'More')]")
                child_btn.click()
                self.driver.implicitly_wait(1)
            except:
                pass

            # exit loop when review quota is reached
            if ite >= GOOGLE_REVIEW_LIMIT:
                break

    def _sort_most_relevant(self):
        """Sort reviews to most relevant reviews"""
        try:
            # use sorting to make the page dynamic - have to first choose most recent reviews to refresh the page
            # then choose most relevant button again - interested in most relevant
            # click sort button
            sort_bt = self.driver.find_element_by_xpath("//button[@aria-label='Sort reviews']")
            sort_bt.click()
            time.sleep(1)

            # first element of the list: most recent
            most_recent_bt = self.driver.find_elements_by_xpath("//li[@role='menuitemradio']")[1]
            most_recent_bt.click()
            time.sleep(1)

            # click sort button
            sort_bt = self.driver.find_element_by_xpath("//button[@aria-label='Sort reviews']")
            sort_bt.click()
            time.sleep(1)

            # second element of the list: most relevant
            most_relevant_bt = self.driver.find_elements_by_xpath("//li[@role='menuitemradio']")[0]
            most_relevant_bt.click()
            time.sleep(1)
        except:
            pass

    def build_loc_reviews(self):
        """Build a list of google reviews based on the location found"""
        if self.place_name:
            logger.info('    Scraping google reviews...')

            # load into reviews page
            self._load_reviews_page()

            # sort reviews to most relevant
            self._sort_most_relevant()

            # scroll reviews to load the contents required based on the number of reviews need to be scraped
            self._scroll()

            # expand reviews
            self._expand_reviews()

            # scrap reviews
            reviews_list = []
            reviews_text = self.driver.find_elements_by_xpath("//span[@class='section-review-text']")
            reviews_ratings = self.driver.find_elements_by_xpath("//span[@class='section-review-stars']")
            published_date = self.driver.find_elements_by_xpath("//span[@class='section-review-publish-date']")

            for ite, review in enumerate(reviews_text, 1):
                # build dictionary
                temp_dict = {'review': review.text}

                try:
                    temp_dict['ratings'] = reviews_ratings[ite - 1].get_attribute('aria-label')
                except:
                    temp_dict['ratings'] = None

                try:
                    temp_dict['date'] = published_date[ite - 1].text
                except:
                    temp_dict['date'] = None

                reviews_list.append(temp_dict)

                # exit loop when review quota is reached
                if ite >= GOOGLE_REVIEW_LIMIT:
                    break
        else:
            reviews_list = []

        return reviews_list
