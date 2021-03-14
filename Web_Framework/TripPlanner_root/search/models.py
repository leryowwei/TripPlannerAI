from django.db import models
from enum import Enum
from cities_light.models import City


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

    # a series of user inputs needed for path planning
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

    # hardcode some values
    flight_class = 'economy'
    sort_flight = 'bestflight_a'

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

class FlightInfo(models.Model):
    price = models.IntegerField()