from django import forms
from django.forms import inlineformset_factory
from .models import Vendor, RFQ, RFQItem, Quotation, QuotationItem


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'company_name', 'contact_person', 'email', 'phone',
            'address', 'city', 'state', 'country', 'pincode',
            'gst_number', 'pan_number', 'category', 'payment_terms',
            'credit_limit', 'rating', 'status', 'notes'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST Number'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN Number'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '5', 'step': '0.1'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class RFQForm(forms.ModelForm):
    class Meta:
        model = RFQ
        fields = [
            'title', 'description', 'category', 'priority', 'deadline',
            'delivery_date', 'delivery_address', 'estimated_budget',
            'terms_and_conditions', 'vendors'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'estimated_budget': forms.NumberInput(attrs={'class': 'form-control'}),
            'terms_and_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'vendors': forms.CheckboxSelectMultiple(),
        }


class RFQItemForm(forms.ModelForm):
    class Meta:
        model = RFQItem
        fields = ['item_name', 'description', 'quantity', 'unit', 'estimated_unit_price', 'specifications']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'estimated_unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'specifications': forms.TextInput(attrs={'class': 'form-control'}),
        }


RFQItemFormSet = inlineformset_factory(
    RFQ, RFQItem, form=RFQItemForm,
    extra=1, can_delete=True,
    min_num=1, validate_min=True
)


class QuotationForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = [
            'rfq', 'vendor', 'gst_percentage', 'discount_percentage',
            'delivery_days', 'payment_terms', 'warranty_period',
            'notes', 'validity_date'
        ]
        widgets = {
            'rfq': forms.Select(attrs={'class': 'form-select'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'gst_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
            'delivery_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_terms': forms.Select(attrs={'class': 'form-select'}),
            'warranty_period': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'validity_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class QuotationItemForm(forms.ModelForm):
    class Meta:
        model = QuotationItem
        fields = ['item_name', 'description', 'quantity', 'unit', 'unit_price']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


QuotationItemFormSet = inlineformset_factory(
    Quotation, QuotationItem, form=QuotationItemForm,
    extra=1, can_delete=True,
    min_num=1, validate_min=True
)