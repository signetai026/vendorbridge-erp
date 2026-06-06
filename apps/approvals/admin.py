from django.contrib import admin
from .models import Vendor, RFQ, RFQItem, Quotation, QuotationItem, ApprovalWorkflow, ApprovalAction


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'contact_person', 'email', 'category', 'status', 'rating']
    list_filter = ['category', 'status']
    search_fields = ['company_name', 'contact_person', 'email']


class RFQItemInline(admin.TabularInline):
    model = RFQItem
    extra = 1


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ['rfq_number', 'title', 'status', 'priority', 'deadline', 'created_by']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['rfq_number', 'title']
    inlines = [RFQItemInline]


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'vendor', 'rfq', 'grand_total', 'status', 'is_selected']
    list_filter = ['status', 'is_selected']
    search_fields = ['quotation_number', 'vendor__company_name']
    inlines = [QuotationItemInline]


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ['rfq', 'quotation', 'current_stage', 'is_active', 'created_at']
    list_filter = ['current_stage', 'is_active']


admin.site.register(ApprovalAction)