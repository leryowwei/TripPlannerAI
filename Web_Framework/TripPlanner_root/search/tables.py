from django_tables2 import tables, TemplateColumn
from .models import FlightInfo, AccomInfo

class FlightInfoTable(tables.Table):
    """Table for flight info"""
    price_per_pas = tables.columns.Column("Price Per Passenger")
    booking_link = tables.columns.URLColumn("View Deal")
    departure = tables.columns.Column("Departure Details")
    arrival = tables.columns.Column("Arrival Details")
    select = TemplateColumn(template_name='button_flight.html')

    class Meta:
        model = FlightInfo
        row_attrs = {
            "data-id": lambda record: record.id
        }
        # prevent these columns from showing
        exclude = ("user_id", "id",)

class AccomInfoTable(tables.Table):
    """Table for Accommodation info"""
    price = tables.columns.Column("Price")
    hotel_name = tables.columns.Column("Hotel Name")
    details = tables.columns.Column("Details")
    #select = TemplateColumn(template_name='button.html')

    class Meta:
        model = AccomInfo
        row_attrs = {
            "data-id": lambda record: record.id
        }
        # prevent these columns from showing
        exclude = ("user_id", "id",)
