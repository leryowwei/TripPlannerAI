# main code to run kayak classes

from FlightQuery import KayakFlight
from AccomQuery import KayakAccom
from selenium import webdriver

# main code
headless = True
webdriver_path = "D:/Documents/GitHub/TripPlannerAI/Miscellaneous/chromedriver_win32/chromedriver.exe"
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
url = 'https://www.kayak.co.uk/flights'
user = {'departure_city': 'Kota Kinabalu',
        'departure_country': 'Malaysia',
        'destination_city': 'Singapore',
        'destination_country': 'Singapore',
        'departure_date': '2021-03-25',
        'return_date': '2021-03-29',
        'adult': 4,
        'children': 0,
        'room': 2,
        'class': 'economy', # economy, business, premium, first
        'sort_flight': 'bestflight_a', #bestflight_a, duration_a, price_a
        'sort_accom': 'rank_a', #distance_a, rank_a, price_a
      }

try:
    option = webdriver.ChromeOptions()
    option.add_argument('window-size=1920x1080')
    option.add_argument("--start-maximized")
    option.add_argument('window-size=1920x1080')
    option.add_argument(f'user-agent={user_agent}')
    if headless:
        # make headless undetectable https://intoli.com/blog/making-chrome-headless-undetectable/
        option.add_argument('headless')
    driver = webdriver.Chrome(executable_path=webdriver_path, options=option)
except:
    raise ValueError("Failed in setting up webdriver. Please check if webdriver is in Miscellaneous folder.")

# (1) Kayak Flight
# initialise object
kf = KayakFlight(driver)

# scrap flight details
url = kf.flight_url_builder(user)
flight_details = kf.scrap_flight_details(url, flightlimit=40)

# (2) Kayak Accommodation
# initialise object
ka = KayakAccom(driver)

# # build accom database
accom_database = ka.build_accom_database(acclimit=20, piclimit=10)

# get accom suggestions
accom_list, accom_database = ka.get_accoms_for_user(user, accom_database, acclimit=10)
