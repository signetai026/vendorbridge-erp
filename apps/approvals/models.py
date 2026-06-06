from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Vendor(models.Model):
    CATEGORY_CHOICES = [
        ('IT', 'IT & Technology'),
        ('OFFICE', 'Office Supplies'),
        ('MANUFACTURING', 'Manufacturing'),
        ('SERVICES', 'Professional Services'),
        ('LOGISTICS', 'Logistics & Transport'),
        ('CONSTRUCTION', 'Construction & Infra'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blacklisted', 'Blacklisted'),
        ('pending', 'Pending Approval'),
    ]

    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10)
    gst_number = models.CharField(max_length=20, blank=True)
    pan_number = models.CharField(max_length=15, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    payment_terms = models.CharField(max_length=100, default='Net 30')
    credit_limit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=3.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_vendors')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company_name']

    def __str__(self):
        return self.company_name

    @property
    def total_po_value(self):
        from purchase_orders.models import PurchaseOrder
        return PurchaseOrder.objects.filter(
            vendor=self, status__in=['approved', 'issued', 'completed']
        ).aggregate(total=models.Sum('total_amount'))['total'] or 0

    @property
    def completed_pos(self):
        from purchase_orders.models import PurchaseOrder
        return PurchaseOrder.objects.filter(vendor=self, status='completed').count()


class RFQ(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('evaluation', 'Under Evaluation'),
        ('awarded', 'Awarded'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    rfq_number = models.CharField(max_length=30, unique=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=Vendor.CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    deadline = models.DateTimeField()
    delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.TextField(blank=True)
    estimated_budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    terms_and_conditions = models.TextField(blank=True)
    vendors = models.ManyToManyField(Vendor, blank=True, related_name='rfqs')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rfqs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rfq_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.rfq_number:
            last = RFQ.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.rfq_number = f"RFQ-{timezone.now().year}-{num:04d}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.deadline

    @property
    def quotation_count(self):
        return self.quotations.count()


class RFQItem(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('ltr', 'Litres'),
        ('mtr', 'Metres'),
        ('box', 'Box'),
        ('set', 'Set'),
        ('unit', 'Unit'),
        ('nos', 'Numbers'),
    ]

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='pcs')
    estimated_unit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    specifications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.rfq.rfq_number} - {self.item_name}"

    @property
    def estimated_total(self):
        if self.estimated_unit_price:
            return self.quantity * self.estimated_unit_price
        return 0


class Quotation(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
    ]
    PAYMENT_TERMS_CHOICES = [
        ('advance', '100% Advance'),
        ('net15', 'Net 15 Days'),
        ('net30', 'Net 30 Days'),
        ('net45', 'Net 45 Days'),
        ('net60', 'Net 60 Days'),
        ('50_50', '50% Advance, 50% on Delivery'),
        ('on_delivery', '100% on Delivery'),
    ]

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='quotations')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='quotations')
    quotation_number = models.CharField(max_length=30, unique=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18.0)
    gst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    delivery_days = models.IntegerField(default=7)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='net30')
    warranty_period = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    validity_date = models.DateField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_selected = models.BooleanField(default=False)

    class Meta:
        ordering = ['grand_total']
        unique_together = ['rfq', 'vendor']

    def __str__(self):
        return f"{self.quotation_number} - {self.vendor.company_name}"

    def save(self, *args, **kwargs):
        if not self.quotation_number:
            last = Quotation.objects.order_by('-id').first()
            num = (last.id + 1) if last else 1
            self.quotation_number = f"QT-{timezone.now().year}-{num:04d}"
        # Auto-calculate amounts
        self.gst_amount = self.subtotal * (self.gst_percentage / 100)
        self.discount_amount = self.subtotal * (self.discount_percentage / 100)
        self.grand_total = self.subtotal + self.gst_amount - self.discount_amount
        super().save(*args, **kwargs)


class QuotationItem(models.Model):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='items')
    rfq_item = models.ForeignKey(RFQItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, default='pcs')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=14, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name


class ApprovalWorkflow(models.Model):
    STAGE_CHOICES = [
        ('submitted', 'Submitted'),
        ('l1_review', 'L1 Manager Review'),
        ('l2_approval', 'L2 Finance Approval'),
        ('procurement_head', 'Procurement Head'),
        ('generate_po', 'Generate PO'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    ACTION_CHOICES = [
        ('submitted', 'Submitted for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('forwarded', 'Forwarded'),
        ('returned', 'Returned for Revision'),
        ('escalated', 'Escalated'),
    ]

    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name='approval_workflows')
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='approval_workflows')
    current_stage = models.CharField(max_length=30, choices=STAGE_CHOICES, default='submitted')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_workflows')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Workflow: {self.rfq.rfq_number} - {self.current_stage}"


class ApprovalAction(models.Model):
    workflow = models.ForeignKey(ApprovalWorkflow, on_delete=models.CASCADE, related_name='actions')
    stage = models.CharField(max_length=30, choices=ApprovalWorkflow.STAGE_CHOICES)
    action = models.CharField(max_length=20, choices=ApprovalWorkflow.ACTION_CHOICES)
    acted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comments = models.TextField(blank=True)
    acted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['acted_at']

    def __str__(self):
        return f"{self.stage} - {self.action} by {self.acted_by}"