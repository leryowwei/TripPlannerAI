
def clean_data(results, location_data, user_class, nlp_loc, driver):
    """ Filter through the keys of the dictionary to extract valid locations and
        information about the location (i.e. ratings) 
    
    """
    # get attributes from user class
    place = user_class.place
    country = user_class.country

    # go through all keys and find out which one to discard
    # if useful key, get all the data
    for key in results:
        # split into words - using nlp loc model
        data = nlp_loc(key)

        # go through object to find entity with label LOC
        for ent in data.ents:

            if ent.label_ == 'LOC':
                keyword = ent.text.strip()
                # ensure text not place or country
                flag = True
                if ent.text.lower().strip() == place or ent.text.lower().strip() == country:
                    flag = False

                # only select keyword that are not in dictionary and are not place/country
                if flag and not keyword in location_data:
                    # get results from google api
                    googleapi_results = check_location_google(keyword, place, country)
                    
                    # got result means we will use the google api name to search foursquare and tripadvisor
                    # also store header and paragraph data and return as a big dictionary
                    if googleapi_results:
                        place_name = googleapi_results['name']

                        print ("Valid location. Keyword {} found to be {}. Building location's database now....".format(keyword, place_name))

                        # get data from foursquare
                        foursquareapi_results = check_location_foursquare_detail(place_name, place, country)

                        # scrap trip advisor website to get reviews and hours
                        tripadvisor_results = extract_ta_data(place_name, user_class, driver)

                        location_data[keyword] = {'name': place_name,
                                                  'google API': googleapi_results,
                                                  'four square API': foursquareapi_results,
                                                  'trip advisor': tripadvisor_results,
                                                  'header': key,
                                                  'paragraph': results[key]}
                
    return location_data