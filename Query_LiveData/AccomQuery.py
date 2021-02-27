# try scraping kayak for accomodation details

import time
import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from kayak import Kayak


class KayakAccom(Kayak):
    def __init__(self, wbdriver):
        """Build kayak scraper class for accomodation"""
        # inherit from parent class
        super().__init__(wbdriver)

    @staticmethod
    def _useraccom_default():
        """ Default user profile for accommodation"""

        # build default user accom profile
        # depart date is one month from today
        # return date is two nights after depart date
        user = {'destination_city': 'Singapore',
                'destination_country': 'Singapore',
                'departure_date': f"{datetime.datetime.now() + datetime.timedelta(days=+31):%Y-%m-%d}",
                'return_date': f"{datetime.datetime.now() + datetime.timedelta(days=+33):%Y-%m-%d}",
                'adult': 2,
                'children': 0,
                'room': 1,
                'sort_accom': 'rank_a',
                }
        return user

    def accom_url_builder(self, user):
        """Constructs the accommodation search url depending on items specified by the user"""
        url = self.base_url

        # TODO: need to implement a series of checksss

        # (1) Destination
        destination = "{},{}".format(user['destination_city'],user['destination_country'])

        # (2) Dates
        # check if date given is valid - got specific format
        self._validate_date(user['departure_date'])
        self._validate_date(user['return_date'])
        # error will be raised - so if we reach this point means no error
        dates = "{}/{}".format(user['departure_date'], user['return_date'])

        # (3) number of people - adult and children
        no_of_ppl = []
        if user['adult'] == 1:
            no_of_ppl.append('1adult')
        else:
            no_of_ppl.append('{}adults'.format(user['adult']))

        # assume all children 11 years old
        if user['children'] > 0:
            no_of_ppl.append('{}children{}'.format(user['children'], '-11' * user['children']))

        no_of_ppl = '/'.join(no_of_ppl)

        # (4) number of rooms - if set as default then let kayak decide
        room = "{}rooms".format(user['room'])

        # (4) sort type (best recommendation, shortest time, cheapest)
        sort_type = user['sort_accom']
        if sort_type not in ['distance_a', 'rank_a', 'price_a']:
            raise ValueError('Sorting type: {} not recognised...'.format(sort_type))

        # build - url dependent of number of rooms
        if user['room'] == 'default':
            url = "{}/hotels/{}/{}/{}?sort={}".format(self.base_url, destination, dates, no_of_ppl, sort_type)
        else:
            url = "{}/hotels/{}/{}/{}/{}?sort={}".format(self.base_url, destination, dates, no_of_ppl, room, sort_type)

        return url

    def build_accom_database(self, acclimit=10, piclimit=5):
        """Scrap accommodation details and build a database - contains name, ratings, description, phone number,
           address, photos

           Steps:
            (1) Build kayak url using standard default user profile - get results based on
            (2) scrap for an x amount of accom depending on the number specified by the user
            (3) return object as a dictionary
        """
        # get url
        url = self.accom_url_builder(self._useraccom_default())

        # load driver to the website and give consent
        self.load_wbdriver(url)

        # load more results
        self.show_more_results(acclimit, 20)

        # get results
        acc_details = {}

        # load x amount of accommodation depends on user specified limit
        for count, ele in enumerate(self.driver.find_elements_by_xpath("//div[@id='searchResultsList']//div[@class='resultWrapper']")):
            # --- start scraping ---
            temp_dict = {}

            # (1) hotel name
            hotel_name = ele.find_element_by_css_selector("span[class='titleContainer']").text
            temp_dict['hotel_name'] = hotel_name

            # jump into detail page to get more information
            # get the window handles using window_handles( ) method
            window_before = self.driver.window_handles[0]

            # click into page to get more details
            ele.find_element_by_css_selector("div[class='col col-title']").find_element_by_css_selector("button").click()

            # get the window handles using window_handles( ) method
            time.sleep(1)
            window_after = self.driver.window_handles[1]

            # switch to new window
            self.driver.switch_to.window(window_after)

            # (2) address
            try:
                address = "{}, {}, {}, {}".format(self.driver.find_element_by_css_selector("span[itemprop='streetAddress']").text,
                                                  self.driver.find_element_by_css_selector("span[itemprop='addressLocality']").text,
                                                  self.driver.find_element_by_css_selector("span[itemprop='postalCode']").text,
                                                  self.driver.find_element_by_css_selector("span[itemprop='addressCountry']").text
                                                  )
            except NoSuchElementException:
                address = None

            temp_dict['address'] = address

            # (3) phone number
            try:
                temp_dict['phone_number'] = self.driver.find_element_by_css_selector("a[class='phone']").text
            except NoSuchElementException:
                temp_dict['phone_number'] = None

            # (4) kayak website
            temp_dict['website'] = self.driver.current_url

            # (5) description
            try:
                temp_dict['description'] = self.driver.find_element_by_css_selector("div[class='overview-container']").text
            except NoSuchElementException:
                temp_dict['description'] = None

            # (6) rating
            try:
                temp_dict['rating'] = self.driver.find_element_by_css_selector("div[class='rating']").text
            except NoSuchElementException:
                temp_dict['rating'] = None

            # (7) pictures - take five first
            images_url = []
            for ite, img_ele in enumerate(self.driver.find_elements_by_xpath("//img")):
                images_url.append(img_ele.get_attribute("src"))

                if ite >= piclimit - 1:
                    break

            temp_dict['images_url'] = images_url

            acc_details[hotel_name] = temp_dict

            # switch back to default window
            self.driver.close()
            self.driver.switch_to.window(window_before)

            # print info
            print("Successfully scraped hotel number {}: {}...".format(count + 1, hotel_name))

            if count >= acclimit - 1:
                break

        return acc_details


# main code
headless = False
webdriver_path = "D:/Documents/GitHub/TripPlannerAI/Miscellaneous/chromedriver_win32/chromedriver.exe"
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
url = 'https://www.kayak.co.uk/flights'
user = {'departure_city': 'Kota Kinabalu',
        'departure_country': 'Malaysia',
        'destination_city': 'Singapore',
        'destination_country': 'Singapore',
        'departure_date': '2021-03-25',
        'return_date': '2021-03-29',
        'adult': 4,
        'children': 0,
        'room': 2,
        'class': 'premium', # economy, business, premium, first
        'sort_flight': 'bestflight_a', #bestflight_a, duration_a, price_a
        'sort_accom': 'rank_a', #distance_a, rank_a, price_a
      }

try:
    option = webdriver.ChromeOptions()
    option.add_argument('window-size=1920x1080')
    option.add_argument("--start-maximized")
    option.add_argument('window-size=1920x1080')
    option.add_argument(f'user-agent={user_agent}')
    if headless:
        # make headless undetectable https://intoli.com/blog/making-chrome-headless-undetectable/
        option.add_argument('headless')
    driver = webdriver.Chrome(executable_path=webdriver_path, options=option)
except:
    raise ValueError("Failed in setting up webdriver. Please check if webdriver is in Miscellaneous folder.")

# initialise object
ka = KayakAccom(driver)

# build accom database
accom_details = ka.build_accom_database(acclimit=40)
print(accom_details)
