""" This module stores all the constants/parameters that are used in the data
    scraper engine.
"""

# API info
google_api_key = 'AIzaSyBMgMsYBSsb7wURHiA6HoQsj1fpQbT9lk8'
foursquare_client_id = 'JV4HQCSP0QY100C1MICQCI5C3XHOVKZSWX1G5IRNSJAZMQFB'
foursquare_client_secret = 'TXWM5UUJPFIFF1J0WML5VDCOEOSZFI2D1PDSTF0LBAGMH3BQ'
here_api_key = 'cYa8I0YLChdxJLX4CffPUM7hfdGqKMegp1dN4mdQ0wc'

# GOOGLE SHEET INFO
# GOOGLE SHEET HERE: https://docs.google.com/spreadsheets/d/1YzKpOIucoUpPXohoF_OjQrKm1Zyas0pVOpgLjqHTcpY/edit#gid=0
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1YzKpOIucoUpPXohoF_OjQrKm1Zyas0pVOpgLjqHTcpY'
GSHEET_DICT = {'sheet': 'Sheet1',
               'foursquare': {'DATE': 'FOURSQUARE_DATE', 'COUNT': 'FOURSQUARE_COUNT'},
               'foursquare_detail': {'DATE': 'FOURSQUARE_DETAIL_DATE', 'COUNT': 'FOURSQUARE_DETAIL_COUNT'},
               'here': {'DATE': 'HERE_DATE', 'COUNT': 'HERE_COUNT'},
               'google': {'DATE': 'GOOGLE_DATE', 'COUNT': 'GOOGLE_COUNT'}}

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