from django.db import models
from django.utils import timezone
from accounts.models import User
 
 
class RFQ(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    rfq_number = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='rfqs_created')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rfqs_assigned')
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'rfq'
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.rfq_number} - {self.title}"
 
    def save(self, *args, **kwargs):
        if not self.rfq_number:
            last = RFQ.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.rfq_number = f"RFQ-{next_id:04d}"
        super().save(*args, **kwargs)
 
    def get_status_badge(self):
        badges = {
            'draft': 'secondary',
            'sent': 'info',
            'received': 'primary',
            'approved': 'success',
            'rejected': 'danger',
            'cancelled': 'warning',
        }
        return badges.get(self.status, 'secondary')
 
 
class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    po_number = models.CharField(max_length=20, unique=True)
    rfq = models.ForeignKey(RFQ, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'purchase_order'
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.po_number}"
 
    def save(self, *args, **kwargs):
        if not self.po_number:
            last = PurchaseOrder.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.po_number = f"PO-{next_id:04d}"
        super().save(*args, **kwargs)
 
    def get_status_badge(self):
        badges = {
            'draft': 'secondary',
            'confirmed': 'primary',
            'shipped': 'info',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return badges.get(self.status, 'secondary')
 
 
class Invoice(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    invoice_number = models.CharField(max_length=20, unique=True)
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
 
    class Meta:
        db_table = 'invoice'
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.invoice_number}"
 
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.invoice_number = f"INV-{next_id:04d}"
        super().save(*args, **kwargs)
 
    def get_status_badge(self):
        badges = {
            'draft': 'secondary',
            'sent': 'info',
            'paid': 'success',
            'overdue': 'danger',
            'cancelled': 'warning',
        }
        return badges.get(self.status, 'secondary')
 
 
class Approval(models.Model):
    TYPE_CHOICES = [
        ('rfq', 'RFQ'),
        ('purchase_order', 'Purchase Order'),
        ('vendor', 'Vendor'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reference_id = models.IntegerField()
    reference_number = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approval_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approval_reviews')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
 
    class Meta:
        db_table = 'approval'
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.reference_number} - {self.title}"
 
    def get_status_badge(self):
        return {'pending': 'warning', 'approved': 'success', 'rejected': 'danger'}.get(self.status, 'secondary')