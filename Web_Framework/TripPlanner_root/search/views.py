from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User, FlightInfo, AccomInfo
from .FlightQuery import KayakFlight
from .AccomQuery import KayakAccom
from .tables import FlightInfoTable
from django.http import Http404
import json

def get_home(request):
    """Show home page for the user"""
    return render(request, 'home.html')

def get_contact_us(request):
    """Show contact us page for the user"""
    return render(request, 'contact.html')

def get_our_story(request):
    """Show our story for the user"""
    return render(request, 'story.html')

def get_userinfo(request):
    """Show form for user to fill in"""
    form = UserForm()

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # save form and access
            newform = form.save()
            return redirect('flight', newform.pk)

    return render(request, 'search.html', {'form': form})


def get_flightinfo(request, pk):
    """Call kayak scraper and show the results to the user for flights"""

    # use primary key to retrive all user inputs from db
    user = User.objects.get(pk=pk)

    # check if user id present in flight info - if present don't need to scrap again
    # sometimes user accidentally clicked refresh but we do not want to scrap the same results again
    flight = FlightInfo.objects.filter(user_id=pk)

    if not flight:
        # establish kayak object
        kayak = KayakFlight(headless=True)

        # build url for kayak
        results = kayak.scrap_flight_details(kayak.flight_url_builder(user), flightlimit=20)
        print(results)

        for x in results:
            FlightInfo.objects.create_flight(pk, x)

    return render(request, 'flight.html', {'flight_list': FlightInfo.objects.filter(user_id=pk)})

def get_accominfo(request, user_id, flight_id):
    """Call kayak scraper and show the results to the user for accommodation"""

    # use primary key to retrive all user inputs from db and store flight id chose by user
    user = User.objects.get(pk=user_id)
    if not FlightInfo.objects.filter(pk=flight_id):
        raise Http404("Flight chose by user does not exist in database! Please restart the search session...")
    user.flight_id = flight_id
    user.save(update_fields=["flight_id"])

    # check if user id present in accom info - if present don't need to scrap again
    # sometimes user accidentally clicked refresh but we do not want to scrap the same results again
    acc = AccomInfo.objects.filter(user_id=user_id)

    if not acc:
        # establish kayak object
        kayak = KayakAccom(headless=True)

        # build url for kayak
        results = kayak.get_accoms_for_user(user, True, acclimit=50, piclimit=20)
        print(results)

        # create accom model
        for accom in results:
            AccomInfo.objects.create_accom(user_id, accom)

    return render(request, 'accom.html', {'accom_list': AccomInfo.objects.filter(user_id=user_id),
                                          'user': User.objects.get(pk=user_id)})

def get_path_planning(request, user_id, accom_id):
    """Call path planning algorithm to plan out the trip"""

    # use primary key to retrive all user inputs from db and store accom id chose by user
    user = User.objects.get(pk=user_id)
    if not AccomInfo.objects.filter(pk=accom_id):
        raise Http404("Accommodation chose by user does not exist in database! Please restart the search session...")
    user.accom_id = accom_id
    user.save(update_fields=["accom_id"])

    # placeholder for path planning code
    # itinerary = path_plan(user)

    return render(request, 'itinerary.html')