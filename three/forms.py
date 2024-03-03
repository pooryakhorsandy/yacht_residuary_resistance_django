#forms.py
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

class RrParametersForm(forms.Form):
    L = forms.FloatField(
        validators=[MinValueValidator(10.0, message='Please enter a number greater than or equal to 10.00'),
                    MaxValueValidator(10.15, message='Please enter a number less than or equal to 10.15')],
        label='Length (L)'
    )
    B = forms.FloatField(
        validators=[MinValueValidator(2.76, message='Please enter a number greater than or equal to 2.76'),
                    MaxValueValidator(3.66, message='Please enter a number less than or equal to 3.66')],
        label='Beam (B)'
    )

    T = forms.FloatField(
        validators=[MinValueValidator(0.64, message='Please enter a number greater than or equal to 0.64'),
                    MaxValueValidator(1.13, message='Please enter a number less than or equal to 1.13')],
        label='Draft (T)'
    )

    def clean(self):
        cleaned_data = super().clean()
        L = cleaned_data.get('L')
        B = cleaned_data.get('B')
        T = cleaned_data.get('T')

        if L is not None and (L < 10.00 or L > 10.15):
            self.add_error('L', 'Please enter the number in the specified range (10.00 to 10.15).')

        if B is not None and (B < 2.76 or B > 3.66):
            self.add_error('B', 'Please enter the number in the specified range (2.76 to 3.66).')

        if T is not None and (T < 0.64 or T > 1.13):
            self.add_error('T', 'Please enter the number in the specified range (0.64 to 1.13).')

        return cleaned_data