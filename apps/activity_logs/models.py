from django.db import models
from django.contrib.auth.models import User


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('vendor_created', 'Vendor Created'),
        ('vendor_updated', 'Vendor Updated'),
        ('vendor_deleted', 'Vendor Deleted'),
        ('rfq_created', 'RFQ Created'),
        ('rfq_published', 'RFQ Published'),
        ('rfq_cancelled', 'RFQ Cancelled'),
        ('quotation_submitted', 'Quotation Submitted'),
        ('quotation_updated', 'Quotation Updated'),
        ('vendor_selected', 'Vendor Selected'),
        ('approval_submitted', 'Submitted for Approval'),
        ('approval_approved', 'Approval Approved'),
        ('approval_rejected', 'Approval Rejected'),
        ('po_generated', 'PO Generated'),
        ('po_issued', 'PO Issued'),
        ('po_completed', 'PO Completed'),
        ('invoice_generated', 'Invoice Generated'),
        ('invoice_paid', 'Invoice Marked Paid'),
        ('report_exported', 'Report Exported'),
        ('comparison_viewed', 'Quotation Comparison Viewed'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    description = models.TextField()
    object_type = models.CharField(max_length=50, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    object_name = models.CharField(max_length=200, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at}"

    @classmethod
    def log(cls, user, action, description, obj=None, request=None, extra=None):
        ip = None
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
        obj_type = ''
        obj_id = None
        obj_name = ''
        if obj:
            obj_type = obj.__class__.__name__
            obj_id = getattr(obj, 'id', None)
            obj_name = str(obj)
        cls.objects.create(
            user=user,
            action=action,
            description=description,
            object_type=obj_type,
            object_id=obj_id,
            object_name=obj_name,
            ip_address=ip,
            extra_data=extra or {}
        )