from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from .FlightQuery import KayakFlight
from .tables import FlightInfoTable
from django_tables2 import RequestConfig

def get_userinfo(request):
    """Show form for user to fill in"""
    form = UserForm()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # save form and access
            newform = form.save()
            return redirect('flight', newform.pk)

    return render(request, 'home.html', {'form': form})


def get_flightinfo(request, pk):
    """Call kayak scraper and show the results to the user"""

    # use primary key to retrive all user inputs from db
    user = User.objects.get(pk=pk)

    # establish kayak object
    kayak = KayakFlight(headless=True)

    # build url for kayak
    results = kayak.scrap_flight_details(kayak.flight_url_builder(user), flightlimit=2)
    print(results)

    # place data in table
    flightinfo = FlightInfoTable(results)
    RequestConfig(request).configure(flightinfo)

    return render(request, 'flight.html', {'flightinfo': flightinfo})

def product(request):
    if request.method=='GET':
        sku = request.GET.get('sku')
        if not sku:
            return render(request, 'inventory/product.html')
        else:
            # now you have the value of sku
            # so you can continue with the rest
            return render(request, 'some_other.html')