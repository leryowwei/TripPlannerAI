#testing file

import requests
import json
import datetime
from urllib import parse

RAPIDAPI_HOST = "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
RAPIDAPI_KEY = "f6407d6a0emsh592d8a450162320p136e87jsn3fec7c5018f7"

class FlightQuery:
    """ Flight price query using skyscanner API provided by rapid API"""

    def __init__(self, params):
        """Initialisation"""
        # unpack inputs
        self.currency = params['currency']
        self.locale = params['locale']
        self.origin = params['origin']
        self.destination = params['destination']
        self.user_country = params['user_country']
        self.outbound_date = params['outbound_date']
        self.inbound_date = params['inbound_date']
        self.direct = params['onlydirect']

        # convert inputs to useful data needed for other methods
        self.user_country_code = self.get_country_code(self.user_country)
        self.origin_id = self.get_placeid(self.origin)
        self.destination_id = self.get_placeid(self.destination)

        # check if dates are correct otherwise raise error
        self._validate_date(self.outbound_date)
        self._validate_date(self.inbound_date)

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
    def _form_url(link, url_params):
        """Combine url and parameters to form a complete url"""
        url_params = "/".join(str(x) for x in url_params)
        if link[-1] == '/':
            return "{}{}/".format(link, url_params)
        else:
            return "{}/{}/".format(link, url_params)

    def get_placeid(self, location):
        """Get the place ID for the location interested"""
        url_params = [self.user_country_code, self.currency, self.locale]
        apicall = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/autosuggest/v1.0/"
        link = self._form_url(apicall, url_params)
        headers = {
            "X-RapidAPI-Host": RAPIDAPI_HOST,
            "X-RapidAPI-Key": RAPIDAPI_KEY,
        }
        querystring = {"query": location}
        r = requests.get(link, headers=headers, params=querystring)
        body = json.loads(r.text)
        places = body['Places']
        top_place_id = places[0]['PlaceId']
        return top_place_id

    def get_country_code(self, country):
        """Get country code"""
        url_params = [self.locale]
        apicall = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/reference/v1.0/countries/"
        link = self._form_url(apicall, url_params)
        headers = {
            "X-RapidAPI-Host": RAPIDAPI_HOST,
            "X-RapidAPI-Key": RAPIDAPI_KEY,
        }
        response = requests.get(link, headers=headers)
        response = json.loads(response.text)
        country_code = [item['Code'] for item in response['Countries'] if item['Name'] == country][0]
        return country_code

    def get_quotes(self):
        """Get quotes based on the user specified information"""
        url_params = [self.user_country_code, self.currency, self.locale, self.origin_id, self.destination_id,
                      self.outbound_date]
        apicall = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browsequotes/v1.0"
        link = self._form_url(apicall, url_params)
        headers = {
            "X-RapidAPI-Host": RAPIDAPI_HOST,
            "X-RapidAPI-Key": RAPIDAPI_KEY,
        }
        querystring = {"inboundpartialdate": str(self.inbound_date)}
        response = requests.request("GET", link, headers=headers, params= querystring)
        return response

# try out code
params = {'user_country': 'United Kingdom',
          'locale': 'en-GB',
          'destination': 'Singapore',
          'origin': 'London, United Kingdom',
          'outbound_date': '2021-01-11',
          'inbound_date': '2021-01-18',
          'currency': 'GBP',
          'onlydirect': False}

fq = FlightQuery(params)
response = fq.get_quotes()

print (response.text)