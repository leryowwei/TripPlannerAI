""" This module stores all the constants/parameters that are used in the data
    scraper engine.
"""

# API info
# API key
foursquare_client_id = 'JV4HQCSP0QY100C1MICQCI5C3XHOVKZSWX1G5IRNSJAZMQFB'
foursquare_client_secret = 'TXWM5UUJPFIFF1J0WML5VDCOEOSZFI2D1PDSTF0LBAGMH3BQ'
here_api_key = 'cYa8I0YLChdxJLX4CffPUM7hfdGqKMegp1dN4mdQ0wc'

# API limit
# limit quoted here are reduced by a few percent to give in some leeway
API_LIMITS = {'foursquare': {'DAY': 1, 'LIMIT': 99000},
              'foursquare_detail': {'DAY': 1, 'LIMIT': 495},
              'here': {'DAY': 30, 'LIMIT': 245000}}

# output data info
TMP_LOCFOUND_NAME = 'TMP_LOCFOUND'
TMP_LOCSCRAPED_NAME = 'TMP_LOCSCRAPED'
NUM_LOC_PER_CSV = 10.0

# trip advisor limit
TA_REVIEW_LIMIT = 5

# google reviews limit
GOOGLE_REVIEW_LIMIT = 200

# latitude and longitude bounds (lat, long) of singapore (hardcoded for now)
COORD_BOUNDS = {'singapore': {'latitude': [1.18, 1.48], 'longitude': [103.58, 104.15]}}

# GOOGLE SHEET INFO
# GOOGLE SHEET HERE: https://docs.google.com/spreadsheets/d/1YzKpOIucoUpPXohoF_OjQrKm1Zyas0pVOpgLjqHTcpY/edit#gid=0
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1YzKpOIucoUpPXohoF_OjQrKm1Zyas0pVOpgLjqHTcpY'
GSHEET_DICT = {'sheet': 'Sheet1',
               'foursquare': {'DATE': 'FOURSQUARE_DATE', 'COUNT': 'FOURSQUARE_COUNT'},
               'foursquare_detail': {'DATE': 'FOURSQUARE_DETAIL_DATE', 'COUNT': 'FOURSQUARE_DETAIL_COUNT'},
               'here': {'DATE': 'HERE_DATE', 'COUNT': 'HERE_COUNT'}}

# default user profile from User class
DEFAULT_USER = {'place':'singapore',
               'country':'singapore',
               'budget': 'n/a',
               'start_date': 'n/a',
               'end_date': 'n/a',
               'departure': 'kuala lumpur',
               'num_people': 2,
               'kids': False,
               'couple': True}