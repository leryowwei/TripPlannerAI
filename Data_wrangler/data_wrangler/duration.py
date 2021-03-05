"""This module goes through the reviews to find out the suggested duration to spend at a place
"""

import numpy as np
import re
from .constants import DURATION_KEYWORDS, FILTER_KEYWORDS
from .utils import form_str, reject_outliers, take_closest_num, logger, find_maxnum_in_str


def convert_str_hours(text):
    """ Convert string to hours

        If text is '###return_hours###', will return the opt_range variable
    """

    # hours
    opt_a = 0.5
    opt_b = 1
    opt_c = 2
    opt_d = 3
    opt_e = 4
    opt_f = 5
    opt_g = 8
    opt_range = [opt_a, opt_b, opt_c, opt_d, opt_e, opt_f, opt_g]

    if text == '###return_hours###':
        return opt_range

    # split to list based on a number of different patterns
    list_of_text = re.split("[+\- ~><]", text)

    # a set of 'if conditions' to decide the hours
    if 'day' in list_of_text and 'half' not in list_of_text and\
            any(x in ['one', 'a', 'all', 'whole', 'entire', 'the', 'full'] for x in list_of_text):
        return opt_g
    elif 'hours' == text:
        return opt_e
    elif any(x in ['hours', 'hour', 'hrs', 'hr'] for x in list_of_text) and\
            any(x in ['several', 'few', 'many'] for x in list_of_text):
        return opt_e
    elif 'afternoon' in list_of_text and any(x in ['a', 'an', 'the'] for x in list_of_text):
        return opt_c
    elif 'morning' in list_of_text and any(x in ['a', 'an', 'the'] for x in list_of_text):
        return opt_c
    elif 'night' in list_of_text and any(x in ['a', 'an', 'the'] for x in list_of_text):
        return opt_c
    elif 'evening' in list_of_text and any(x in ['a', 'an', 'the'] for x in list_of_text):
        return opt_c
    elif any(x in ['a', 'an', 'the'] for x in list_of_text) and any(x in ['hour', 'hr'] for x in list_of_text):
        return opt_b
    elif 'half' in list_of_text and 'day' in list_of_text:
        return opt_f
    elif 'couple' in list_of_text and any(x in ['hour', 'hr', 'hours', 'hrs'] for x in list_of_text):
        return opt_c
    elif any(x in ['min', 'minute', 'mins', 'minutes'] for x in list_of_text):
        minutes = find_maxnum_in_str(text)
        if minutes:
            hrs = minutes / 60.0
            return take_closest_num(hrs, opt_range)
    elif any(x in ['hour', 'hr', 'hours', 'hrs'] for x in list_of_text):
        hrs = find_maxnum_in_str(list_of_text)
        if hrs:
            return take_closest_num(hrs, opt_range)
    elif any(x in ['day', 'days'] for x in list_of_text):
        days = find_maxnum_in_str(list_of_text)
        if days:
            # assume one day is 8 hours
            hrs = days * opt_g

            # ignore anything greater than a day - TODO need to improve
            if hrs <= opt_g:
                return take_closest_num(hrs, opt_range)
    else:
        return None


def find_duration_of_loc(loc_dict, nlp):
    """Find out the suggested duration for a location based on the reviews, tips, paragraphs and descriptions provided

       Steps taken:
       - if suggested duration by tripadvisor not available, go through the reviews and find the durations.
       - A mean of all durations found from review will be calculated. The mean which is closest to the options available
         (options can be found in the function convert_str_to_hours) will be chosen.
       - The duration found will be checked against the hardcoded durations which are based on tags.
       - Depending on the venue's priority, different actions will be taken:
       - (1) High priority venue: the duration found needs to be within 20% of the hardcoded value. Otherwise,
        set to the hardcoded value.
       - (2) Low priority venue: If the duration exceeds the tag's hardcoded durations, the hardcoded durations will be
       used and a message will be logged for troubleshooting.
    """
    # TODO: Obviously there are a lot of flaws in the logic/ algorithm here...we need to think about more improvements
    # only go through the process if suggested duration not found from tripadvisor
    if loc_dict['suggested_duration'] in ['N/A', None]:
        # access hardcoded duration and find out the priority
        hardcoded_duration = loc_dict['hardcoded_durations_value']
        priority = loc_dict['hardcoded_durations_priority']

        # extract information about duration from tips, reviews, paragraphs and descriptions
        text = form_str([loc_dict['foursquare_description'], loc_dict['paragraph'], loc_dict['combined_reviews_tips']])
        doc = nlp(text)

        # split into sentences using nlp and find out entities related to data or time
        entities = []
        for i, token in enumerate(doc.sents):
            # if contains the duration keywords (spend, took) but does not contain filter keywords (wait, queue)
            # then take the entities
            if any(x in token.text.lower() for x in DURATION_KEYWORDS) and not \
                    any(x in token.text.lower() for x in FILTER_KEYWORDS):
                for ent in token.ents:
                    if ent.label_ == 'TIME' or ent.label_ == 'DATE':
                        # only accept the entity when it is positioned after the verb
                        entities.append(ent.text)
        temp_results = []
        # convert all entities in list to actual hours
        for ite in entities:
            hours = convert_str_hours(ite)
            # only store not None
            if hours:
                temp_results.append(hours)

        # return the results: before that, reject outliers and find out the mode
        if temp_results:
            # reject outliers from list
            temp_results = reject_outliers(temp_results)

            # find out the mean time in the list
            mean_hour = np.mean(temp_results)

            # get list of hour options available, not the best way to do this
            # TODO: improve this
            opt_range = convert_str_hours('###return_hours###')

            # assign the value closest to the opt_range
            duration = take_closest_num(mean_hour, opt_range)

            # check duration against upper bound hardcoded values and its priority
            # (1) if it is high priority, the duration found needs to be within 20% of the hardcoded value. Otherwise,
            # set to the hardcoded value.
            # (2) if it is low priority, take the duration found from review unless it exceeds the upper bound value.
            # if exceeds, take the hardcoded value.
            if hardcoded_duration:
                if priority:
                    lower_limit = hardcoded_duration - hardcoded_duration * 0.2
                    upper_limit = hardcoded_duration + hardcoded_duration * 0.2

                    if duration < lower_limit or duration > upper_limit:
                        logger.info("High priority venue: Suggested duration for {} from reviews, which is {} hours, "
                                    "outside of hardcoded duration range {}-{}. Hardcoded duration: {} to be used...".
                                    format(loc_dict['name'], duration, lower_limit, upper_limit, hardcoded_duration))
                        duration = hardcoded_duration
                    else:
                        logger.info("High priority venue: Suggested duration for {} found to be {} hours from reviews".
                                    format(loc_dict['name'], duration))
                else:
                    if duration > hardcoded_duration:
                        logger.info("Suggested duration for {} from reviews, which is {} hours, "
                                    "exceeds hardcoded duration of {} hours. Hardcoded duration to be used...".
                                    format(loc_dict['name'], duration, hardcoded_duration))
                        duration = hardcoded_duration
                    else:
                        logger.info("Suggested duration for {} found to be {} hours from reviews".
                                    format(loc_dict['name'], duration))
        else:
            # nothing found so have to use hardcoded value for this
            duration = hardcoded_duration

        # assign value back to master dictionary
        loc_dict['suggested_duration'] = duration

    return loc_dict
