# try scraping kayak for accomodation details

import time
import datetime
from selenium.common.exceptions import NoSuchElementException
from kayak import Kayak


class KayakAccom(Kayak):
    def __init__(self, headless=True):
        """Build kayak scraper class for accomodation"""
        # inherit from parent class
        super().__init__(headless)

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

    @staticmethod
    def _url_destination(user):
        """Return destination for url based on yser profile"""
        return "{},{}".format(user['destination_city'], user['destination_country'])

    def _url_dates(self, user):
        """Return dates for url based on user profile"""
        # check if date given is valid - got specific format
        self._validate_date(user['departure_date'])
        self._validate_date(user['return_date'])
        # error will be raised - so if we reach this point means no error
        dates = "{}/{}".format(user['departure_date'], user['return_date'])

        return dates

    @staticmethod
    def _url_people(user):
        """Return number of people for url based on user profile"""

        no_of_ppl = []
        if user['adult'] == 1:
            no_of_ppl.append('1adult')
        else:
            no_of_ppl.append('{}adults'.format(user['adult']))

        # assume all children 11 years old
        if user['children'] > 0:
            no_of_ppl.append('{}children{}'.format(user['children'], '-11' * user['children']))

        no_of_ppl = '/'.join(no_of_ppl)

        return no_of_ppl

    @staticmethod
    def _url_rooms(user):
        """Return number of rooms for url based on user profile"""
        return "{}rooms".format(user['room'])

    @staticmethod
    def _url_sort(user):
        """Return sort filter for url based on user profile"""
        # (4) sort type (best recommendation, shortest time, cheapest)
        sort_type = user['sort_accom']
        if sort_type not in ['distance_a', 'rank_a', 'price_a']:
            raise ValueError('Sorting type: {} not recognised...'.format(sort_type))
        return sort_type

    def accom_url_builder(self, user):
        """Constructs the accommodation search url depending on items specified by the user"""
        # (1) Destination
        destination = self._url_destination(user)

        # (2) Dates
        dates = self._url_dates(user)

        # (3) number of people - adult and children
        no_of_ppl = self._url_people(user)

        # (4) number of rooms - if set as default then let kayak decide
        room = self._url_rooms(user)

        # (4) sort type (best recommendation, shortest time, cheapest)
        sort_type = self._url_sort(user)

        # build - url dependent of number of rooms
        if room == 'default':
            url = "{}/hotels/{}/{}/{}?sort={}".format(self.base_url, destination, dates, no_of_ppl, sort_type)
        else:
            url = "{}/hotels/{}/{}/{}/{}?sort={}".format(self.base_url, destination, dates, no_of_ppl, room, sort_type)

        return url

    def _get_accom_detail(self, ele, piclimit):
        """Get details of a specific accommodation represented by the element passed in"""

        # --- start scraping info about the location
        temp_dict = {}

        # (1) hotel name
        hotel_name = ele.find_element_by_css_selector("span[class='titleContainer']").text
        temp_dict['hotel_name'] = hotel_name

        # (2) number of stars
        try:
            temp_dict['stars'] = ele.find_element_by_css_selector("div[class=' col col-stars']").\
                find_element_by_css_selector("div[aria-label*='Rating Score']").get_attribute("data-count")
        except NoSuchElementException:
            temp_dict['stars'] = None

        # jump into detail page to get more information
        # get the window handles using window_handles( ) method
        window_before = self.driver.window_handles[0]

        # click into page to get more details
        ele.find_element_by_css_selector("div[class='col col-title']").find_element_by_css_selector(
            "button").click()

        # get the window handles using window_handles( ) method
        time.sleep(1)
        window_after = self.driver.window_handles[1]

        # switch to new window
        self.driver.switch_to.window(window_after)

        # (3) address
        try:
            address = "{}, {}, {}, {}".format(
                self.driver.find_element_by_css_selector("span[itemprop='streetAddress']").text,
                self.driver.find_element_by_css_selector("span[itemprop='addressLocality']").text,
                self.driver.find_element_by_css_selector("span[itemprop='postalCode']").text,
                self.driver.find_element_by_css_selector("span[itemprop='addressCountry']").text
            )
        except NoSuchElementException:
            address = None

        temp_dict['address'] = address

        # (4) phone number
        try:
            temp_dict['phone_number'] = self.driver.find_element_by_css_selector("a[class='phone']").text
        except NoSuchElementException:
            temp_dict['phone_number'] = None

        # (5) kayak website - remove info about searches
        details_url = self.driver.current_url
        temp_dict['website'] = details_url[:details_url.find('-details/') + 9]

        # (6) description
        try:
            temp_dict['description'] = self.driver.find_element_by_css_selector(
                "div[class='overview-container']").text
        except NoSuchElementException:
            temp_dict['description'] = None

        # (7) rating
        try:
            temp_dict['rating'] = self.driver.find_element_by_css_selector("div[class='rating']").text
        except NoSuchElementException:
            temp_dict['rating'] = None

        # (8) pictures
        images_url = []
        try:
            for ite, img_ele in enumerate(self.driver.find_elements_by_xpath("//img")):
                images_url.append(img_ele.get_attribute("src"))

                if ite >= piclimit - 1:
                    break
        except NoSuchElementException:
            pass

        temp_dict['images_url'] = images_url

        # (9) check in, check out time
        try:
            for policy in self.driver.find_element_by_css_selector("section[aria-label='Policies"). \
                    find_elements_by_css_selector("div[class='box']"):

                if 'check in' in policy.text.lower():
                    temp_dict['check_in'] = policy.text.split("\n")[-1]
                elif 'check out' in policy.text.lower():
                    temp_dict['check_out'] = policy.text.split("\n")[-1]
        except NoSuchElementException:
            # if fail, it might be in different format
            # try scraping different stuff
            try:
                policy = self.driver.find_element_by_css_selector("div[data-code='checkinCheckout']").\
                    find_element_by_css_selector("div[class='Fa11-description']").text
                temp_dict['check_in'] = policy.split(",")[0].split(" ")[-1]
                temp_dict['check_out'] = policy.split(",")[1].split(" ")[-1]
            except NoSuchElementException:
                temp_dict['check_in'] = None
                temp_dict['check_out'] = None

        # switch back to default window
        self.driver.close()
        self.driver.switch_to.window(window_before)

        return temp_dict

    def get_accoms_for_user(self, user, accom_database, acclimit=10, piclimit=5):
        """Scrap to get real time prices of accomodation depends on the user profile

           Also store details of the accommodation from database into the return dictionary

           If details of the specific accommodation has not been built, details will be scraped on the spot
        """
        # get url
        url = self.accom_url_builder(user)

        # load driver to the website and give consent
        self.load_wbdriver(url)

        # load more results
        self.show_more_results(acclimit, 20)

        # get results
        accom_list = {}

        # load x amount of accommodation depends on user specified limit
        for count, ele in enumerate(
                self.driver.find_elements_by_xpath("//div[@id='searchResultsList']//div[@class='resultWrapper']")):

            temp_dict = {}

            # (1) hotel name
            hotel_name = ele.find_element_by_css_selector("span[class='titleContainer']").text
            temp_dict['hotel_name'] = hotel_name

            # (2) price
            temp_dict['price'] = ele.find_element_by_css_selector("div[id*='booking-price']").text

            # check if hotel already in database, otherwise build database and store it back
            if hotel_name not in accom_database:
                accom_database[hotel_name] = self._get_accom_detail(ele, piclimit)
                print("Database for {} not available. It's now successfully added to the database...".format(hotel_name))

            # store hotel details to dictionary
            temp_dict['details'] = accom_database[hotel_name]

            # edit the website to be relevant based on user profile
            temp_dict['details']['website'] = "{}/{}/{}/{}".format(temp_dict['details']['website'],
                                                                   self._url_dates(user),
                                                                   self._url_people(user),
                                                                   self._url_rooms(user))

            # store to master dict
            accom_list[hotel_name] = temp_dict

            if count >= acclimit - 1:
                break

        return accom_list, accom_database

    def build_accom_database(self, acclimit=10, piclimit=5):
        """Scrap accommodation details and build a database - contains name, ratings, description, phone number,
           address, photos

           Steps:
            (1) Build kayak url using standard default user profile - get results based on
            (2) scrap for an x amount of accom depending on the number specified by the user
            (3) return database as dict
        """
        # get url
        url = self.accom_url_builder(self._useraccom_default())

        # load driver to the website and give consent
        self.load_wbdriver(url)

        # load more results
        self.show_more_results(acclimit, 20)

        # store results
        accom_details = {}

        # load x amount of accommodation depends on user specified limit
        for count, ele in enumerate(
                self.driver.find_elements_by_xpath("//div[@id='searchResultsList']//div[@class='resultWrapper']")):

            # get details of the accomodation
            temp_dict = self._get_accom_detail(ele, piclimit)
            hotel_name = temp_dict['hotel_name']

            # store back to master dict
            accom_details[hotel_name] = temp_dict

            # print info
            print("Successfully scraped hotel number {}: {}...".format(count + 1, hotel_name))

            if count >= acclimit - 1:
                break

        return accom_details
