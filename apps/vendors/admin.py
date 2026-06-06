from django.contrib import admin
from .models import Vendor, VendorCategory, VendorDocument, VendorActivity
 
 
@admin.register(VendorCategory)
class VendorCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
 
 
@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['vendor_code', 'vendor_name', 'company_name', 'category', 'status', 'rating', 'city', 'created_at']
    list_filter = ['status', 'rating', 'category', 'country']
    search_fields = ['vendor_name', 'company_name', 'email', 'vendor_code']
    readonly_fields = ['vendor_code', 'created_at', 'updated_at']
    ordering = ['-created_at']
    list_per_page = 25
    fieldsets = (
        ('Basic Info', {'fields': ('vendor_code', 'vendor_name', 'company_name', 'category')}),
        ('Tax Info', {'fields': ('gst_number', 'pan_number')}),
        ('Contact', {'fields': ('contact_person', 'email', 'phone', 'alternate_phone', 'website')}),
        ('Address', {'fields': ('address', 'city', 'state', 'country', 'pincode')}),
        ('Status & Rating', {'fields': ('status', 'rating')}),
        ('Banking', {'fields': ('bank_name', 'bank_account', 'bank_ifsc')}),
        ('Notes', {'fields': ('notes',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
 
 
@admin.register(VendorDocument)
class VendorDocumentAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'doc_type', 'name', 'uploaded_at']
    list_filter = ['doc_type']
 
 
@admin.register(VendorActivity)
class VendorActivityAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'action', 'performed_by', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']