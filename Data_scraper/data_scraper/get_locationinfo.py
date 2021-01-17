""" This module gets information of a specific location by accessing APIs and
    scraping google maps.
"""

from . import constants
from .access_api import check_location_foursquare, check_location_foursquare_detail, check_location_here
from .gmaps import GoogleMapsLocationInfo, GoogleMapsLocationReview
from .utils import read_cell, write_cell, logger, write_output_json, check_within_country
from .extract_ta import extract_ta_data
from datetime import datetime, date, timezone

def check_limit(gsheet, api_type):
    """ Check usage limit of the api 
        
        if current date in the Googlse sheet already passed the limit date, 
        update with today's date and reset quota.
    """

    # get data from google sheet
    access_date = read_cell(gsheet, api_type, 'DATE')
    access_date = datetime.strptime(access_date.replace("'", ""), '%Y-%m-%d %H:%M:%S')
    usage = int(read_cell(gsheet, api_type, 'COUNT'))
    
    # find out how many days since (compare to UTC timezone)
    current_time = datetime.now(timezone.utc).replace(tzinfo=None)
    time_between = current_time - access_date
    
    # convert to days
    time_between = time_between.total_seconds() / (60 * 60 * 24)
    
    # find out limits and refresh days
    api_days = constants.API_LIMITS[api_type]['DAY']
    api_limit = constants.API_LIMITS[api_type]['LIMIT']

    # check if limit is reached
    if time_between <= api_days and usage < api_limit:
        flag = True
    elif time_between > api_days:
        # get midnight of today's date
        today = date.today()
        midnight = datetime.combine(today, datetime.min.time())
        
        # if date expired, update with today's date midnight and reset quota
        write_cell(gsheet, api_type, 'DATE', "'" + str(midnight))
        write_cell(gsheet, api_type, 'COUNT', 0)
        flag = True                
    else:
        logger.error('API Limit reached for {}.'.format(api_type))
        flag = False
        
    return flag
    
def get_locationinfo(scraped_location, location_found, user_class, driver, gsheet, api_type, output_path, ta_review_limits,
                     google_review_limits):
    """ Access google, tripadvisor and APIs to build location's information
    
        Steps:
            (1) Dump out a tmp file with all the location data first
            (2) Start building database whilst monitoring the API limit
            (3) After building data for each location, the data will be dumped out as a pickle file.
    
        Note: if the API limits are reached, code will be terminated but the user can continue the progress
        again. Before terminating, the code will dump out two TMP files to allow the user to continue again next time.
        
    """
    # get attributes from user class
    place = user_class.place
    country = user_class.country
    
    # initiation
    checked_list = []
    quota_flag = False

    for count, keyword in enumerate(scraped_location, 1):
        # check google maps to see if it's a legit place. Otherwise, give a recommendation
        gmaps_info = GoogleMapsLocationInfo(driver, "{} {} {}".format(keyword, place, country))

        # read attributes
        place_name = gmaps_info.place_name
        coord = gmaps_info.get_coordinates()
        url = gmaps_info.url

        # check country of location
        country_flag = False
        if coord:
            if check_within_country(user_class, coord):
                country_flag = True

        # carry on if it is a legit place and the location is in the same country
        if place_name and country_flag:
            # make sure no repeatitive data        
            if place_name not in location_found:
                # put in a big try.. except
                try:
                    logger.info("{}. Valid location. Keyword {} found to be {}. Building location's database now....".format(count, keyword, place_name))
                    
                    # check if api limit is reached          
                    # special case for foursquare detail
                    if api_type == 'foursquare_detail':               
                        # need to check two apis
                        flag_1 = check_limit(gsheet, api_type)
                        flag_2 = check_limit(gsheet, 'foursquare')
                        flag = flag_1 == flag_2
                    else:
                        flag = check_limit(gsheet, api_type)
                        
                    # continue getting data from api if limit not yet reached
                    if flag:
                        # build database for location using google maps
                        gmaps_database = gmaps_info.build_loc_database()

                        # gather google reviews for location
                        gmaps_review = GoogleMapsLocationReview(driver, url, place_name, google_review_limits)
                        gmaps_database['reviews'] = gmaps_review.build_loc_reviews()

                        # get data from api depending on user input
                        if api_type == 'foursquare':
                            api_data = check_location_foursquare(place_name, place, country, gsheet)
                        elif api_type == 'foursquare_detail':
                            api_data = check_location_foursquare_detail(place_name, place, country, gsheet)
                        elif api_type == 'here':
                            api_data = check_location_here(place_name, place, country, gsheet)

                        # get reviews and suggested duration from trip advisor
                        ta_dict = extract_ta_data(place_name, user_class, driver, ta_review_limits)

                        # get existing data from the old dictionary
                        temp_dict = scraped_location[keyword]
                        
                        # store other data
                        temp_dict['name'] = gmaps_info.place_name
                        temp_dict['Google_data'] = gmaps_database
                        temp_dict['TripAdvisor_data'] = ta_dict
                        temp_dict['API_used'] = api_type
                        temp_dict['API_data'] = api_data
                        
                        # dump data out as json file
                        write_output_json(temp_dict, output_path, place_name)
                        
                        # add location to the location found list
                        location_found.append(gmaps_info.place_name)
                        
                        logger.info('-------------------------------------------------------------------')
                    else:
                        # quota reached. Exit from for loop
                        quota_flag = True
                        break                    
                except:
                    logger.exception('Error occur while building database for keyword: {}, place: {}. Skip to next keyword...'.format(keyword, place_name))
                    logger.info('-------------------------------------------------------------------')
            else:        
                logger.info("{}. Data already exists for keyword {}. Skip to next keyword....".format(count, keyword))
                logger.info('-------------------------------------------------------------------')
        else:
            logger.info("{}. Location not found for keyword {}....".format(count, keyword))
            logger.info('-------------------------------------------------------------------')
            
        # store to dictionary as this keyword has been checked
        checked_list.append(keyword)
    
    # limit is reached so cannot extract data anymore
    if quota_flag:
        logger.error("API access for {} terminated due to limit reached. Please continue the code once the quota is refreshed.".format(api_type))
        
        # remove the keywords from dictionary to be dumped out
        new_scraped_loc = {}
        for key in scraped_location:
            if key not in checked_list:
                new_scraped_loc[key] = scraped_location[key]
                
        # dump out location data and new location as json file
        write_output_json(new_scraped_loc, output_path, constants.TMP_LOCSCRAPED_NAME)
        write_output_json(location_found, output_path, constants.TMP_LOCFOUND_NAME)
    
        logger.error("Temporary files at current step written to output folder. Rerun the code when the quota is renewed " + 
                     "and the code will continue to get API data from where the code terminated.")       
                
    return quota_flag