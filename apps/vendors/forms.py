
from django import forms
from .models import Vendor, VendorCategory, VendorDocument
 
 
class VendorCategoryForm(forms.ModelForm):
    class Meta:
        model = VendorCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
        }
 
 
class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = [
            'vendor_name', 'company_name', 'category', 'gst_number', 'pan_number',
            'contact_person', 'email', 'phone', 'alternate_phone', 'website',
            'address', 'city', 'state', 'country', 'pincode',
            'rating', 'status',
            'bank_name', 'bank_account', 'bank_ifsc',
            'notes',
        ]
        widgets = {
            'vendor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vendor Name'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST Number'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN Number'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Person'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Alternate Phone'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://website.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Number'}),
            'bank_ifsc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC Code'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional Notes'}),
        }
 
 
class VendorFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Search vendors...'
    }))
    category = forms.ModelChoiceField(
        queryset=VendorCategory.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Vendor.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    rating = forms.ChoiceField(
        choices=[('', 'All Ratings')] + [(str(i), f'{i} Stars') for i in range(1, 6)],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Filter by city...'
    }))
 
 
class VendorDocumentForm(forms.ModelForm):
    class Meta:
        model = VendorDocument
        fields = ['doc_type', 'name', 'file']
        widgets = {
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document Name'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }