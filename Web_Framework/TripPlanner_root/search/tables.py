from django_tables2 import tables, TemplateColumn
from .models import FlightInfo

class FlightInfoTable(tables.Table):
    """Table for flight info"""
    price_per_pas = tables.columns.Column("Price Per Passenger")
    booking_link = tables.columns.URLColumn("View Deal")
    departure = tables.columns.Column("Departure Details")
    arrival = tables.columns.Column("Arrival Details")
    select = TemplateColumn(template_name='button.html')
    # <!--  <a class="btn btn-info btn-sm" href="{% url 'training_update' record.id %}">Open</a> -->