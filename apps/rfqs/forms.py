# apps/rfqs/forms.py

from django import forms
from .models import RFQ


class RFQForm(forms.ModelForm):
    class Meta:
        model = RFQ
        fields = [
            'title',
            'description',
            'quantity',
            'deadline',
            'status',
        ]