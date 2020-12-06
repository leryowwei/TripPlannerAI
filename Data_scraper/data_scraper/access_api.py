""" This module allows the user to extract information of a location based on a
    keyword supplied using APIs. Information extracted including address, opening hours etc.
    
    The data are returned in the form of dictionary.
    
    APIs available are:
        (1) Google API - WARNING running on FREE credit
        (2) Foursquare detail API - Premium endpoint and limited to 500 pulls per day
        (3) Foursquare API - 90,000 per day but limited info
        (4) Here API - 250K per month

"""
    
import requests
import json
import herepy
import constants

def check_location_google(keyword, place, country):
    """ Find out the actualy place based on the keyword using google api
    
        WARNING: THIS IS CURRENTLY RUNNING ON FREE CREDIT. ONCE FREE CREDIT IS RUN OUT,
        WE WILL NEED TO PAY
        
        More information about the api: https://developers.google.com/places/web-service/details
    
    """
    keyword = "{} {} {}".format(keyword, place, country)

    # basic fields which do not need to pay    
    fields = ['name', 'formatted_address', 'permanently_closed', 'business_status', 
              'place_id', 'type']
    
    api_key = constants.google_api_key
    
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input="+ keyword + \
          "&inputtype=textquery&fields=" + ",".join(fields) + "&key="+ api_key 
          
    response = requests.get(url).json()

    try:
      #only take the first result
      results = response['candidates'][0]
    except:
      results = {}

    return results

def check_location_foursquare_detail(keyword, place, country):
    """Checks if the name of place given corresponds to a place on the foursquare API

      if valid place, non empty dict will be returned. This includes all details of
      the place.

      WARNING: THIS IS A PREMIUM PULL - 500 calls limit per day
    
    """
    # start with regular call to find out the place's place ID first
    url = 'https://api.foursquare.com/v2/venues/search'

    params = dict(
              client_id = constants.foursquare_client_id,
              client_secret= constants.foursquare_client_secret,
              v='20200819', #version date
              near='{} {}'.format(place, country),
              query=keyword,
              limit=1 
              )

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)

    # get place id
    try:
      place_id = data['response']['venues'][0]['id']

      # perform detail search on foursquare - premium call using the place_id
      url = 'https://api.foursquare.com/v2/venues/' + place_id

      params = dict(
                client_id = constants.foursquare_client_id,
                client_secret= constants.foursquare_client_secret,
                v='20200819'
                )

      resp = requests.get(url=url, params=params)
      data = json.loads(resp.text)
    except:
      print ('Place ID not found for keyword: ' + keyword)
      place_id = 'None'

    # return dictionary
    if place_id != 'None':
        result = data
    else:
        result = {}

    return result

def check_location_foursquare(keyword, place, country):
    """Checks if the name of place given corresponds to a place on the foursquare API

      if valid place, non empty list with values will be returned
    
    """
    url = 'https://api.foursquare.com/v2/venues/search'

    params = dict(
              client_id = constants.foursquare_client_id,
              client_secret= constants.foursquare_client_secret,
              v='20200819', #version date
              near='{} {}'.format(place, country),
              query=keyword,
              limit=1 
              )

    resp = requests.get(url=url, params=params)
    data = json.loads(resp.text)

    # take first item
    x = data['response']

    # if no name then return empty list
    result = []
    # form basic list of results to return 
    if x:
      if x['venues']:
        try:
          result.append(x['venues'][0]['name'])
        except:
          raise ValueError('Name missing for key: ' + keyword)

        try:
          result.append(x['venues'][0]['location']['formattedAddress'])
        except:
          result.append([])

        try:
          result.append(x['venues'][0]['categories'])
        except:
          result.append([])
      else:
        result = []
    else:
      result = []

    return result

def check_location_here(keyword, place, country):
    """Checks if the name of place given corresponds to a place on the HERE API

      if valid place, non empty list with values will be returned
    
    """
    keyword = '{} {} {}'.format(keyword, place, country)

    # 250k searches limit per month
    placesApi = herepy.PlacesApi(constants.here_api_key)
    response = placesApi.onebox_search([50,50], keyword)

    # take first item
    x = response.items[0]

    # no results then return empty list
    result = []

    # form basic list of results to return for now
    if x:
      try:
        result.append(x['title'])
      except:
        raise ValueError('Title not found for key: ' + place)

      try:
        result.append(x['address'])
      except:
        result.append([])

      try:
        result.append(x['categories'])
      except:
        result.append([])

      try:
        result.append(x['position'])
      except:
        result.append([])

      try:
        result.append(x['openingHours'])
      except:
        result.append([])

    else:
      result = []

    return result