# try scraping kayak for flight details

import pandas as pd
from kayak import Kayak

class KayakFlight(Kayak):
    def __init__(self, wbdriver):
        """Build kayak scraper class for flights"""
        super().__init__(wbdriver)

        # read in IATA code csv file as pandas df
        # TODO: need to update link to be modular
        self.iata_df = pd.read_csv("D:/Documents/GitHub/TripPlannerAI/Miscellaneous/airport_codes_iata_only.csv")

    def get_iata_code(self, destination):
        """Get IATA code for a place"""
        # TODO: need to do destination check or take the closest destination
        return self.iata_df.loc[self.iata_df['municipality'] == destination, 'iata_code'].iloc[0]

    def flight_url_builder(self, user):
        """Constructs the flight search url depending on items specified by the user"""
        url = self.base_url

        # TODO: need to implement a series of checksss

        # (1) Departure and destination places
        code_name = "{}-{}".format(self.get_iata_code(user['departure_city']),
                                   self.get_iata_code(user['destination_city']))

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

        if user['children'] > 0:
            no_of_ppl.append('children{}'.format('-11' * user['children']))

        no_of_ppl = '/'.join(no_of_ppl)

        # (3) flight class type
        flight_class = user['class']
        if flight_class not in ['economy', 'premium', 'business', 'first']:
            raise ValueError('Flight class: {} not recognised...'.format(flight_class))

        # (4) sort type (best recommendation, shortest time, cheapest)
        sort_type = user['sort_flight']
        if sort_type not in ['bestflight_a', 'duration_a', 'price_a']:
            raise ValueError('Sorting type: {} not recognised...'.format(sort_type))

        # build url
        url = "{}/flights/{}/{}/{}/{}?sort={}".format(self.base_url, code_name, dates, no_of_ppl, flight_class, sort_type)

        return url

    @staticmethod
    def _get_flight_leg_details(element):
        """Get detail information of the leg of flight"""

        flight_leg = {}

        # get depart and arrival time
        try:
            flight_leg['depart_time'] = element.find_element_by_css_selector("span[class='depart-time base-time']").text
            flight_leg['arrival_time'] = element.find_element_by_css_selector("span[class='arrival-time base-time']").text
        except:
            pass

        # find out section stop details
        try:
            flight_leg['stop_number'] = element.find_element_by_css_selector("span[class^='stops-text']").text
            flight_leg['layovers'] = element.find_element_by_css_selector("span[class='js-layover']").text
        except:
            pass

        # find out duration
        try:
            duration = element.find_element_by_css_selector("div[class='section duration allow-multi-modal-icons']").\
                find_element_by_css_selector("div[class='top']").text
            flight_leg['duration'] = duration
        except:
            pass

        # find out carriers (might have more than 1)
        try:
            flight_leg['carrier'] = []
            carriers = element.find_element_by_css_selector("div[class='section stacked-carriers']").\
                find_elements_by_css_selector("div[class='leg-carrier']")
            for ele in carriers:
                ele = ele.find_element_by_css_selector("img")
                # remove the word logo
                flight_leg['carrier'].append(ele.get_attribute('alt')[:-5])
        except:
            pass

        return flight_leg

    def scrap_flight_details(self, url, flightlimit=10):
        """Scrap flight details from the url provided"""
        # load driver to the website and give consent
        self.load_wbdriver(url)

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
            temp_details['departure'] = self._get_flight_leg_details(departure)
            # arrival
            arrival = ele.find_element_by_css_selector("li[class='flight ']")
            temp_details['arrival'] = self._get_flight_leg_details(arrival)

            flight_details.append(temp_details)

            if count >= flightlimit - 1:
                break

        return flight_details