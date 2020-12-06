""" This module cleans the data scrape from the websites to get the location
    name. It returns a location_data dictionary.
"""

def clean_data(website_data, nlp_loc, user_class):
    """ Go through the headers obtained from all websites and store the valid 
        location to dictionary
    
        For each header, run NLP to extract the 'LOC' entity from the header.
        The code will run through some basic filtering on the entity extracted.
        
        Valid entity will be stored in the dictionary together with the paragraph
        and website associated to the header.
    """
    # get attributes from user class
    place = user_class.place
    country = user_class.country
    
    count = 0

    # go through all keys and find out which one to discard
    # if useful key, setup dictionary to store API data later
    for website in website_data:
        results = website_data[website]
        
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
                        location_data[keyword] = {'website': website,
                                                  'header': key,
                                                  'paragraph': results[key]}
                        
                        count += 1
    
    print ("A total of {} headers/keywords found....".format(count))   
        
    return location_data

