"""This module post-processes the location dictionary which has been unpacked """

from .utils import logger
from .constants import MIN_REVIEW_RATINGS, RESTAURANT_PRICES


def combine_reviews_tips(reviews, tips):
    """Combine all reviews and customer tips into one big string"""
    combined_string = []

    # filter and combine reviews first
    # TODO: add date filter
    for i in reviews:
        review = i['review']
        # TODO: spelling problem will be fixed in datascraper
        try:
            ratings = i['ratings']
        except KeyError:
            ratings = i['rating']
        # only consider reviews that are above the minimum requirement and reviews cannot be empty
        if int(ratings) >= MIN_REVIEW_RATINGS and review not in ['', None, 'N/A']:
            combined_string.append(review)

    # add tips to list
    if tips:
        combined_string.extend(tips)

    # combine the whole list into one big string and return them
    return ' '.join(combined_string)

def reformat_reviews(result_dict):
    # TODO: need to convert date as well - need to think of a way to do that
    for count, review in enumerate(result_dict['reviews']):
        # TODO: spelling problem will be fixed in datascraper
        try:
            rating = review['ratings']
        except KeyError:
            rating = review['rating']

        # google reviews contain stars and is from a range of 1-5 so multiply them with 10
        # if review is null or none, set it to zero
        if rating:
            if 'star' in rating:
                rating = [int(i) for i in rating.split() if i.isdigit()][0]
                rating = rating * 10
        else:
            rating = 0

        result_dict['reviews'][count]['ratings'] = rating
    return result_dict

def convert_tripadvisor_duration(result_dict):
    """Converts tripadvisor duration from string with range to solid integer number"""

    duration = result_dict['suggested_duration']

    # convert string to integer if it exists
    if duration not in [None, 'n/a', 'N/A']:
        duration = duration.lower()
        if '< 1' in duration:
            duration = 1
        elif '1-2' in duration:
            duration = 2
        elif '2-3' in duration:
            duration = 3
        elif 'more than 3' in duration:
            duration = 4
        else:
            raise ValueError('Trip Advisor duration: {}, not recognised...'.format(duration))

    return duration

def add_tags(result_dict, venue_categories):
    """Find out the tags that are associated to each location based on their categories"""

    # unpack venue categories dict to get individual dataframe
    google_cat_df = venue_categories['google']
    foursquare_cat_df = venue_categories['foursquare']

    # get categories for google and foursquare
    google_cat = result_dict['category']
    foursquare_cat = result_dict['foursquare_category']

    # find tags
    tags = []
    tags_name = ('Tag_1', 'Tag_2', 'Tag_3', 'Tag_4')

    if google_cat:
        # get all tag data for the category
        tag_row = google_cat_df.loc[google_cat_df['Categories'] == google_cat, tags_name]

        if len(tag_row) > 0:
            tags.extend(list(tag_row.iloc[0, :]))

    if foursquare_cat:
        # get all tag data for the category
        tag_row = foursquare_cat_df.loc[foursquare_cat_df['Categories'] == foursquare_cat, tags_name]

        if len(tag_row) > 0:
            tags.extend(list(tag_row.iloc[0, :]))

    # remove duplicates
    tags = list(dict.fromkeys(tags))

    # remove NaN from the list
    if 'nan' in tags:
        tags.remove('nan')

    return tags

def add_hardcoded_duration(result_dict, venue_categories):
    """Find out the hardcoded duration from the venue categories dataframe based on the tags"""

    # unpack venue categories dict to get duration dataframe
    tag_dur_df = venue_categories['tag_duration']

    # go through tags and find out their duration
    # two sets of values required: normal duration and high priority durations if they exist
    dur_list = []
    high_priority_dur_list = []

    for tag in result_dict['tags']:
        dur, priority = tag_dur_df.loc[tag_dur_df['Tag'] == tag, ('Duration', 'Duration_Priority')].iloc[0]

        if dur != 'nan':
            if priority == 'h':
                high_priority_dur_list.append(float(dur))
            else:
                dur_list.append(float(dur))

    # find out the final duration - max value from the list
    # if high priority exists, take the maximum value from high priority
    # return as dictionary and set priority to true if it's a high priority place
    if high_priority_dur_list:
        return {'duration': max(high_priority_dur_list), 'priority': True}
    elif dur_list:
        return {'duration': max(dur_list), 'priority': False}
    else:
        return {'duration': None, 'priority': False}

def pp_dict(result_dict, venue_categories):
    """Data clean dictionary and post-process the dictionary to add more data like tags, prices, durations etc.
       Items:
       (1) convert review ratings to standardise values
       (2) combine reviews and tips into one new key
       (3) convert suggested duration from tripadvisor to fix hours
       (4) assign venue tag to location. For example, 'restaruant' is a tag and consists of all different categories of
       restaurants


    """
    # (1) reformat the reviews so that both google and trip advisor data are standardised
    result_dict = reformat_reviews(result_dict)

    # (2) combine different texts (reviews and tips) into one big string
    result_dict['combined_reviews_tips'] = combine_reviews_tips(result_dict['reviews'],
                                                                result_dict['customer_tips_review'])

    # (3) Convert durations from reviews to hours
    result_dict['suggested_duration'] = convert_tripadvisor_duration(result_dict)

    # (4) convert pricing tiers to price value for restaurants
    if result_dict['price']:
        result_dict['price_value'] = RESTAURANT_PRICES[result_dict['price'].lower()]
    else:
        result_dict['price_value'] = None

    # (5) convert categories to lower case
    if result_dict['category']:
        result_dict['category'] = result_dict['category'].lower()

    if result_dict['foursquare_category']:
        result_dict['foursquare_category'] = result_dict['foursquare_category'].lower()

    # (5) add tags to the venue based on the category of location
    result_dict['tags'] = add_tags(result_dict, venue_categories)

    # (6) add hardcoded duration based on tag
    result_dict['hardcoded_durations'] = add_hardcoded_duration(result_dict, venue_categories)

    return result_dict
