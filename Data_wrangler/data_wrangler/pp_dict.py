"""This module post-processes the location dictionary which has been unpacked """

from .utils import logger, convert_12hr_to_24hr_timerange
from .constants import MIN_REVIEW_RATINGS, RESTAURANT_PRICES, DAYS_IN_A_WEEK


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
    # return the duration and priority level
    if high_priority_dur_list:
        return max(high_priority_dur_list),  True
    elif dur_list:
        return max(dur_list), False
    else:
        return None, False


def unpack_foursquare_hours(result_dict, key_to_read, key_to_write):
    """Unpacks foursquare hours"""

    # get current dictionary value out and delete the key
    timeframe = result_dict[key_to_read]
    del result_dict[key_to_read]

    # start finding out the data
    reformatted_time = [[]] * 7

    # if data exists then store time into list
    if timeframe:
        for ite, item in enumerate(timeframe):
            # skip the first item
            if ite > 0:
                # get the days
                list_of_days = item['days'].split("–")

                # find out list of times
                list_of_times = []
                for time in item['open']:
                    # convert to 24 hr system before appending to list
                    list_of_times.append(convert_12hr_to_24hr_timerange(time['renderedTime']))

                # store data
                for day in list_of_days:
                    # find out which position of list to store
                    reformatted_time[DAYS_IN_A_WEEK.index(day)] = list_of_times

    # assign time back into result dictionary
    for ite, day in enumerate(DAYS_IN_A_WEEK):
        key = "{}_for_{}".format(key_to_write, day.lower())
        result_dict[key] = reformatted_time[ite]

    return result_dict


def unpack_google_hours(result_dict, key_to_read, key_to_write):
    """Unpacks google hours"""

    # get current dictionary value out and delete the key
    timeframes = result_dict[key_to_read]
    del result_dict[key_to_read]

    # start unpacking
    if timeframes:
        reformatted_time = [[]] * 7
        for item in timeframes:
            temp_list = item.split(",")
            day, time = temp_list[0:2]
            # convert to 24 hour system
            reformatted_time[DAYS_IN_A_WEEK.index(day[0:3])] = convert_12hr_to_24hr_timerange(time)

    # assign time back into result dictionary
    for ite, day in enumerate(DAYS_IN_A_WEEK):
        key = "{}_for_{}".format(key_to_write, day.lower())
        result_dict[key] = reformatted_time[ite]

    return result_dict


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
    result_dict['hardcoded_durations_value'], result_dict['hardcoded_durations_priority'] = add_hardcoded_duration(result_dict, venue_categories)

    # (7) unpack popular times properly (this is from foursquare)
    result_dict = unpack_foursquare_hours(result_dict, "popular_timeframes", "popular_time")

    # (7) unpack opening hours properly (this is either from foursquare or google)
    if result_dict['hours']:
        result_dict = unpack_google_hours(result_dict, "hours", "hours")
        del result_dict['foursquare_hours']
    else:
        result_dict = unpack_foursquare_hours(result_dict, "foursquare_hours", "hours")
        del result_dict['hours']

    return result_dict
