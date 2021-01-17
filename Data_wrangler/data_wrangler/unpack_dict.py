"""This module reads in the location dictionary, unpacks it and extracts the items interested """

from .utils import logger


def unpack_dict(loc_dict):
    """Combine data from google, tripadvisor and API into a standardised dictionary. Only taking the items that we want
    """
    # unpack dictionary first
    name = loc_dict['name']
    google_data = loc_dict['Google_data']
    tripadvisor_data = loc_dict['TripAdvisor_data']
    api_data = loc_dict['API_data']

    # take items from google, tripadvisor and foursquare detail api
    # [1] google data: name, coordinates, ratings, address, website, phone_number, price, plus_code, hours,
    # category, reviews
    result_dict = google_data

    # [2] miscellaneous data - paragraph info from website
    result_dict['paragraph'] = [loc_dict['paragraph']]

    # before getting data from tripadvisor and API - pre-define keys to dictionary
    labels = ['suggested_duration', 'tripadvisor_url', 'foursquare_description', 'foursquare_category', 'instagram',
              'customer_tips_review', 'popular_timeframes']

    for label in labels:
        result_dict[label] = None

    # [3] tripadvisor data: hours (suggested duration), tripadvisor url
    if tripadvisor_data:
        result_dict['suggested_duration'] = tripadvisor_data['hours']
        result_dict['tripadvisor_url'] = tripadvisor_data['url']
        result_dict['reviews'].extend(tripadvisor_data['reviews'])

    # [4] foursquare detail data: description, category, contacts, customer tips reviews, popular visiting hours,
    # pricing (if google data is empty)
    if api_data:
        api_data = api_data['response']['venue']

        # description
        try:
            result_dict['foursquare_description'] = [api_data['description']]
        except KeyError:
            logger.debug('foursquare instagram not found for {}'.format(name))

        # category
        try:
            result_dict['foursquare_category'] = api_data['categories'][0]['name'].lower()
        except (KeyError, IndexError):
            logger.debug('foursquare category not found for {}'.format(name))

        # contact instagram
        try:
            result_dict['instagram'] = api_data['contact']['instagram']
        except KeyError:
            logger.debug('foursquare instagram not found for {}'.format(name))

        # Customer Tips Review
        reviews = []
        try:
            for i in api_data['tips']['groups'][0]['items']:
                reviews.append(i['text'])
            result_dict['customer_tips_review'] = reviews
        except (KeyError, IndexError):
            logger.debug('foursquare customer tips not found for {}'.format(name))

        # Popular visiting hours:
        try:
            result_dict['popular_timeframes'] = api_data['popular']['timeframes']
        except KeyError:
            logger.debug('foursquare popular timeframes not found for {}'.format(name))

        # price
        if not result_dict['price']:
            try:
                result_dict['price'] = api_data['price']['message']
            except KeyError:
                logger.debug('foursquare price data not found for {}'.format(name))

    return result_dict




