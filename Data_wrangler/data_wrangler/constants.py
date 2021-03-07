""" This module stores all the constants/parameters that are used in the data wrangler engine
"""
# ---------- Data related to foursquare/google ----------
# prices (cheap is for foursquare, inexpensive is for google)
RESTAURANT_PRICES = {'cheap': 15, 'inexpensive': 15, 'moderate': 30, 'expensive': 40, 'very expensive': 50}

# ---------- Word Finder constants --------------
# only want couples and not couple cause couple can mean couple hours
# couples would be lemmatized to 'couple', however, I have removed 'couple' at stopword pipeline.
ROMANTIC_LIST = ['romantic', 'love', 'amorous', 'intimate', 'passionate', 'lovey-dovey',
                 'fairy-tale', 'anniversary', 'monthsary', 'date', 'loved one',
                 'significant other', 'couples', 'couple']

NATURE_LIST = ['nature', 'animal', 'plant', 'garden', 'flora', 'tree', 'flower',
               'lake', 'river', 'mountain', 'hike', 'trail', 'aquatic', 'aquarium',
               'zoo', 'creature', 'marine', 'sea', 'beach', 'ocean', 'fauna', 'botanical',
               'tropical', 'forest']

RELAX_LIST = ['relax', 'idyllic', 'peaceful', 'tranquil', 'zen', 'peace', 'calm',
              'soothing', 'chill', 'slow pace', 'quiet', 'oasis']

FAMILY_LIST = ['family', 'child', 'children', 'kid', 'family-friendly']

ADVENTURE_LIST = ['adventure', 'adventurous', 'adrenaline', 'thrill', 'thrill-seekers',
                  'roller coaster', 'exciting', 'fun filled', 'heart pumping',
                  'thrilling', 'arenaline junkie', 'bungee jump']

SHOPPING_LIST = ['shopping', 'shop', 'mall', 'deal', 'buy', 'retail', 'retailer',
                 'boutique', 'brand', 'sale', 'outlet', 'purchase', 'clothing',
                 'clothes', 'souvenirs', 'trinkets', 'item', 'fashion']

NIGHTLIFE_LIST =['nightlife', 'bar', 'bars', 'drink', 'drinks', 'sip', 'club',
                 'music', 'dj', 'techno', 'rnb', 'party', 'late night', 'clubbing', 'dance',
                 'dancing', 'night out', 'cocktail', 'cocktails', 'gin', 'whiskey', 'tequila']

FOODIE_LIST = ['foodie', 'food', 'cafe', 'eat', 'delicious', 'lunch', 'dinner', 'restaurant',
               'restaurants', 'tasty', 'taste', 'meal']

CULTURAL_LIST = ['cultural', 'culture', 'heritage', 'art', 'antique', 'UNESCO',
                 'architecture', 'medieval', 'museum', 'gallery', 'exhibit', 'sculpture', 'painting']

# dictionary for each label
WORD_FINDER_LABELS = {'romantic': ROMANTIC_LIST, 'nature': NATURE_LIST, 'family': FAMILY_LIST,
                      'adventure': ADVENTURE_LIST, 'shopping': SHOPPING_LIST, 'relax': RELAX_LIST,
                      'nightlife': NIGHTLIFE_LIST, 'foodie': FOODIE_LIST, 'cultural': CULTURAL_LIST}

# remove 'couple', and adding couple to romantic tag, as 'couples' would be lemmatized to 'couple'
MY_STOPWORDS = ['singapore','i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
                "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her',
                'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
                'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be',
                'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but',
                'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on',
                'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
                'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd',
                'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
                'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
                'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't",
                'wouldn', "wouldn't", "couple"]

# ---------- Other constants --------------
ADDRESS_LIMIT = 50
NAME_LIMIT = 50

MIN_REVIEW_RATINGS = 30

DURATION_KEYWORDS = ['spend', 'spent', 'took']
FILTER_KEYWORDS = ['queue', 'wait']
TIME_PERIOD = ['AM', 'PM']

# 24 hour system
STRING_TO_TIME_MAPPING = {'NOON': '12:00', 'MIDNIGHT': '24:00', 'MORNING': '09:00',
                          'EVENING': '19:00', 'CLOSED': None, 'NONE': None}

DAYS_IN_A_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']