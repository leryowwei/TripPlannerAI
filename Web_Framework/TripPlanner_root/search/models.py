from django.db import models
from enum import Enum
from cities_light.models import City
from django_mysql.models import ListCharField
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class User(models.Model):
    """Base class for user"""
    class BUDGET(Enum):
        low = ('low', 'Cheapest possible trip - maximise things to do')
        intermediate = ('intermediate', 'Comfortable trip')
        high = ('high', 'Luxury trip - budget is not an issue')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    # (1) a series of user inputs needed for path planning
    no_of_adults = models.IntegerField(default=1)
    no_of_children = models.IntegerField(default=0)
    departure_date = models.DateField()
    return_date = models.DateField()
    departure_city = models.ForeignKey(City, on_delete=models.DO_NOTHING, related_name='departure_city')
    # limit destination to singapore only (id can be found in sql database)
    destination_city = models.ForeignKey(City, on_delete=models.DO_NOTHING,
                                         limit_choices_to={'id': 1}, related_name='destination_city')
    budget = models.CharField(max_length=12,
                              choices=[x.value for x in BUDGET], default=BUDGET.get_value('intermediate'))

    # (2) hardcode some values to be used by flight and accom scrapers
    flight_class = 'economy'
    sort_flight = 'bestflight_a'
    no_of_rooms = 'default'
    sort_accom = 'rank_a'

    # (3) store ids for flight and accom chose by the user
    flight_id = models.IntegerField(default=0)
    accom_id = models.IntegerField(default=0)

    def get_str_departure_city(self):
        """Return string value of the city"""
        return str(self.departure_city).split(", ")[0]

    def get_str_destination_city(self):
        """Return string value of the city"""
        return str(self.destination_city).split(", ")[0]

    def get_str_departure_country(self):
        """Return string value of the country"""
        return str(self.departure_city).split(", ")[0]

    def get_str_destination_country(self):
        """Return string value of the country"""
        return str(self.destination_city).split(", ")[0]

    def get_no_of_nights(self):
        """Return string value of number of nights"""
        delta = self.return_date - self.departure_date
        return str(delta.days)


class FlightInfoManager(models.Manager):
    def create_flight(self, user_id, flight_dict):
        flight = self.create(user_id=user_id,
                             price_per_pas=flight_dict['price_per_pas'],
                             booking_link=flight_dict['booking_link'],
                             departure_depart_time=flight_dict['departure_depart_time'],
                             arrival_depart_time=flight_dict['arrival_depart_time'],
                             departure_arrival_time=flight_dict['departure_arrival_time'],
                             arrival_arrival_time=flight_dict['arrival_arrival_time'],
                             departure_stop_number=flight_dict['departure_stop_number'],
                             arrival_stop_number=flight_dict['arrival_stop_number'],
                             departure_layovers=flight_dict['departure_layovers'],
                             arrival_layovers=flight_dict['arrival_layovers'],
                             departure_duration=flight_dict['departure_duration'],
                             arrival_duration=flight_dict['arrival_duration'],
                             departure_carrier=flight_dict['departure_carrier'],
                             arrival_carrier=flight_dict['arrival_carrier'],
                             departure_logo_url=flight_dict['departure_logo_url'],
                             arrival_logo_url=flight_dict['arrival_logo_url'],
                             departure_depart_airport=flight_dict['departure_depart_airport'],
                             departure_arrival_airport=flight_dict['departure_arrival_airport'],
                             arrival_depart_airport=flight_dict['arrival_depart_airport'],
                             arrival_arrival_airport=flight_dict['arrival_arrival_airport'],)

        # do something with the book
        return flight


class FlightInfo(models.Model):
    user_id = models.IntegerField(default='0')
    price_per_pas = models.CharField(max_length=100, null=True)
    booking_link = models.URLField(max_length=5000, null=True)
    # time
    departure_depart_time = models.CharField(max_length=100, null=True)
    arrival_depart_time = models.CharField(max_length=100, null=True)
    departure_arrival_time = models.CharField(max_length=100, null=True)
    arrival_arrival_time = models.CharField(max_length=100, null=True)
    # number of stops
    departure_stop_number = models.CharField(max_length=50, null=True)
    arrival_stop_number = models.CharField(max_length=50, null=True)
    # airports to layover
    departure_layovers = models.CharField(max_length=200, null=True)
    arrival_layovers = models.CharField(max_length=200, null=True)
    #duration
    departure_duration = models.CharField(max_length=50, null=True)
    arrival_duration = models.CharField(max_length=50, null=True)
    # carrier names
    departure_carrier = models.CharField(max_length=200, null=True)
    arrival_carrier = models.CharField(max_length=200, null=True)
    # logo
    departure_logo_url = ArrayField(models.CharField(max_length=1000), null=True)
    arrival_logo_url = ArrayField(models.CharField(max_length=1000), null=True)
    # airport
    departure_depart_airport = models.CharField(max_length=200, null=True)
    departure_arrival_airport = models.CharField(max_length=200, null=True)
    arrival_depart_airport = models.CharField(max_length=200, null=True)
    arrival_arrival_airport = models.CharField(max_length=200, null=True)

    objects = FlightInfoManager()


class AccomInfoManager(models.Manager):
    def create_accom(self, user_id, accom_dict):

        accom = self.create(user_id=user_id,
                            hotel_name=accom_dict['hotel_name'],
                            price=accom_dict['price'],
                            stars=accom_dict['stars'],
                            address=accom_dict['address'],
                            phone_number=accom_dict['phone_number'],
                            website=accom_dict['website'],
                            images_url=accom_dict['images_url'],
                            description=accom_dict['description'],
                            rating=accom_dict['rating'],
                            check_in=accom_dict['check_in'],
                            check_out=accom_dict['check_out'])

        # do something with the book
        return accom

class AccomDatabaseManager(models.Manager):
    def create_accom(self, accom_dict):

        accom = self.create(hotel_name=accom_dict['hotel_name'],
                            stars=accom_dict['stars'],
                            address=accom_dict['address'],
                            phone_number=accom_dict['phone_number'],
                            website=accom_dict['website'],
                            images_url=accom_dict['images_url'],
                            description=accom_dict['description'],
                            rating=accom_dict['rating'],
                            check_in=accom_dict['check_in'],
                            check_out=accom_dict['check_out'])

        # do something with the book
        return accom

class AccomInfo(models.Model):
    user_id = models.IntegerField(default='0')
    price = models.CharField(max_length=100, null=True)
    hotel_name = models.CharField(max_length=1000, null=True)
    stars = models.IntegerField(null=True)
    address = models.CharField(max_length=1000, null=True)
    phone_number = models.CharField(max_length=100, null=True)
    website = models.URLField(max_length=5000, null=True)
    images_url = ArrayField(models.CharField(max_length=1000), null=True)
    description = models.CharField(max_length=50000, null=True)
    rating = models.CharField(max_length=5, null=True)
    check_in = models.TimeField(null=True)
    check_out = models.TimeField(null=True)
    objects = AccomInfoManager()

class AccomDatabase(models.Model):
    hotel_name = models.CharField(max_length=1000, null=True)
    stars = models.IntegerField(null=True)
    address = models.CharField(max_length=1000, null=True)
    phone_number = models.CharField(max_length=100, null=True)
    website = models.URLField(max_length=5000, null=True)
    images_url = ArrayField(models.CharField(max_length=1000), null=True)
    description = models.CharField(max_length=50000, null=True)
    rating = models.CharField(max_length=5, null=True)
    check_in = models.TimeField(null=True)
    check_out = models.TimeField(null=True)
    objects = AccomDatabaseManager()

