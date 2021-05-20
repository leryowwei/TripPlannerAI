from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from .models import User
from datetime import datetime

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['no_of_adults', 'no_of_children', 'departure_date', 'return_date', 'departure_city',
                  'destination_city', 'budget']
        widgets = {
            'departure_date': DatePickerInput(format='%Y-%m-%d'), # specify date-frmat
            'return_date': DatePickerInput(format='%Y-%m-%d'), # specify date-frmat
        }
        exclude = ("flight_id", "accom_id",)

    def clean(self):
        """Clean data and raise error if results are invalid"""
        super(forms.ModelForm, self).clean()

        departure_date = self.cleaned_data["departure_date"]
        return_date = self.cleaned_data["return_date"]
        departure_city = self.cleaned_data["departure_city"]
        destination_city = self.cleaned_data["destination_city"]

        # check date - if correct convert to string
        if departure_date <= datetime.now().date():
            raise forms.ValidationError("Departure date cannot be from the same day/ from the past.")
        elif departure_date > return_date:
            raise forms.ValidationError("Departure date cannot be later than return date.")
        else:
            self.cleaned_data["departure_date"] = departure_date.strftime('%Y-%m-%d')
            self.cleaned_data["return_date"] = return_date.strftime('%Y-%m-%d')

        # check number of people
        if self.cleaned_data["no_of_adults"] + self.cleaned_data["no_of_children"] == 0:
            raise forms.ValidationError("Both adults and children cannot be zero.")

        # check cities - if correct, replace the city and country
        if departure_city == destination_city:
            raise forms.ValidationError("Departure city and destination city cannot be the same.")

        return self.cleaned_data
