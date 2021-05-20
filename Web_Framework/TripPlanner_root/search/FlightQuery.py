# try scraping kayak for flight details

import pandas as pd
from .kayak import Kayak
from selenium.common.exceptions import NoSuchElementException

class KayakFlight(Kayak):
    def __init__(self, headless=True):
        """Build kayak scraper class for flights"""
        super().__init__(headless)

        # read in IATA code csv file as pandas df
        # TODO: need to update link to be modular
        self.iata_df = pd.read_csv("D:/Documents/GitHub/TripPlannerAI/Miscellaneous/airport_codes_iata_only.csv")

    def get_iata_code(self, destination):
        """Get IATA code for a place"""
        # TODO: need to do destination check or take the closest destination
        return self.iata_df.loc[self.iata_df['municipality'] == destination, 'iata_code'].iloc[0]

    def flight_url_builder(self, user):
        """Constructs the flight search url depending on items specified by the user"""

        # (1) Departure and destination places
        code_name = "{}-{}".format(self.get_iata_code(user.get_str_departure_city()),
                                   self.get_iata_code(user.get_str_destination_city()))

        # (2) Dates
        dates = "{}/{}".format(user.departure_date, user.return_date)

        # (3) number of people - adult and children
        no_of_ppl = []
        if user.no_of_adults == 1:
            no_of_ppl.append('1adult')
        else:
            no_of_ppl.append('{}adults'.format(user.no_of_adults))

        if user.no_of_children > 0:
            no_of_ppl.append('children{}'.format('-11' * user.no_of_children))

        no_of_ppl = '/'.join(no_of_ppl)

        # (3) flight class type
        flight_class = user.flight_class
        if flight_class not in ['economy', 'premium', 'business', 'first']:
            raise ValueError('Flight class: {} not recognised...'.format(flight_class))

        # (4) sort type (best recommendation, shortest time, cheapest)
        sort_type = user.sort_flight
        if sort_type not in ['bestflight_a', 'duration_a', 'price_a']:
            raise ValueError('Sorting type: {} not recognised...'.format(sort_type))

        # build url
        url = "{}/flights/{}/{}/{}/{}?sort={}".format(self.base_url, code_name, dates, no_of_ppl, flight_class, sort_type)

        print(url)

        return url

    @staticmethod
    def _get_flight_leg_details(element, journey):
        """Get detail information of the leg of flight"""

        flight_leg = {}

        # get depart and arrival time
        try:
            flight_leg['{}_depart_time'.format(journey)] = element.find_element_by_css_selector("div[class='section times']").\
                find_element_by_css_selector("span[class='depart-time base-time']").text
            flight_leg['{}_arrival_time'.format(journey)] = element.find_element_by_css_selector("div[class='section times']").\
                find_element_by_css_selector("span[class='arrival-time base-time']").text
        except NoSuchElementException:
            flight_leg['{}_depart_time'.format(journey)] = ""
            flight_leg['{}_arrival_time'.format(journey)] = ""

        # find out section stop details
        try:
            # see direct flight exists
            flight_leg['{}_stop_number'.format(journey)] = element.find_element_by_css_selector("div[class='section stops']").\
                find_element_by_css_selector("span[class='stops-text']").text
            flight_leg['{}_layovers'.format(journey)] = ""
        except NoSuchElementException:
            try:
                flight_leg['{}_stop_number'.format(journey)] = element.find_element_by_css_selector("div[class='section stops']").\
                    find_element_by_css_selector("span[class^='stops-text']").text
                flight_leg['{}_layovers'.format(journey)] =  element.find_element_by_css_selector("div[class='section stops']").\
                    find_element_by_css_selector("span[class='js-layover']").text
            except NoSuchElementException:
                flight_leg['{}_stop_number'.format(journey)] = ""
                flight_leg['{}_layovers'.format(journey)] = ""

        # find out duration
        try:
            duration = element.find_element_by_css_selector("div[class='section duration allow-multi-modal-icons']").\
                find_element_by_css_selector("div[class='top']").text
            flight_leg['{}_duration'.format(journey)] = duration
        except NoSuchElementException:
            flight_leg['{}_duration'.format(journey)] = ""

        # find out carriers and logos (might have more than 1)
        try:
            tmp_carrier_names = []
            tmp_carrier_logos = []
            carriers = element.find_element_by_css_selector("div[class='section stacked-carriers']").\
                find_elements_by_css_selector("div[class='leg-carrier']")
            for ele in carriers:
                ele = ele.find_element_by_css_selector("img")
                # remove the word logo
                tmp_carrier_names.append(ele.get_attribute('alt')[:-5])
                tmp_carrier_logos.append(ele.get_attribute('src'))
            flight_leg['{}_carrier'.format(journey)] = ",".join(tmp_carrier_names)
            flight_leg['{}_logo_url'.format(journey)] = tmp_carrier_logos
        except NoSuchElementException:
            flight_leg['{}_carrier'.format(journey)] = ""
            flight_leg['{}_logo_url'.format(journey)] = []

        # find out airports
        try:
            airports = element.find_element_by_css_selector("div[class='section times']").\
                find_elements_by_css_selector("span[class='airport-name']")

            # check if airport not two elements
            if len(airports) != 2:
                raise ValueError("Number of airports not two for {}".format(airports))

            flight_leg['{}_depart_airport'.format(journey)] = airports[0].text
            flight_leg['{}_arrival_airport'.format(journey)] = airports[1].text
        except NoSuchElementException:
            flight_leg['{}_depart_airport'.format(journey)] = ""
            flight_leg['{}_arrival_airport'.format(journey)] = ""

        return flight_leg

    def scrap_flight_details(self, url, flightlimit=10):
        """Scrap flight details from the url provided"""
        # load driver to the website and give consent
        self.load_wbdriver(url)

        # TODO: Need to implement traps in case no data is found or same day flight not found yadayada.... (IMPORTANT)

        # load more results
        self.show_more_results(flightlimit, 16)

        # get the results
        flight_details = []

        for count, ele in enumerate(self.driver.find_elements_by_xpath("//div[@id='searchResultsList']//div[@class='resultWrapper']")):
            temp_details = {}

            # --- start scraping ---
            # price per pax
            temp_details['price_per_pas'] = ele.find_element_by_css_selector("span.price-text").text
            # link to book
            temp_details['booking_link'] = ele.find_element_by_css_selector("a.booking-link").get_attribute("href")
            # departure
            departure = ele.find_element_by_css_selector("li[class='flight with-gutter']")
            temp_details.update(self._get_flight_leg_details(departure, 'departure'))
            # arrival
            arrival = ele.find_element_by_css_selector("li[class='flight ']")
            temp_details.update(self._get_flight_leg_details(arrival, 'arrival'))

            flight_details.append(temp_details)

            if count >= flightlimit - 1:
                break

        return flight_details
