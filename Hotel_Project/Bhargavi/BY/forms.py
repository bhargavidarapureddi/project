from django import forms

class BookingForm(forms.Form):
    location = forms.CharField(max_length=50)
    room_type = forms.CharField(max_length=12)
    hotel = forms.CharField(max_length=50)
    check_in = forms.DateField(label='Check-in Date')
    check_out = forms.DateField(label='Check-out Date')
    price = forms.DecimalField(label='Price', required=False)

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out date must be after Check-in date.")

        return cleaned_data
