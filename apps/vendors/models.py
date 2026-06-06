
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
 
 
class VendorCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'vendor_category'
        verbose_name_plural = 'Vendor Categories'
        ordering = ['name']
 
    def __str__(self):
        return self.name
 
 
class Vendor(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Blocked'),
        ('pending', 'Pending Approval'),
    ]
 
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
 
    vendor_code = models.CharField(max_length=20, unique=True, editable=False)
    vendor_name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    category = models.ForeignKey(VendorCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendors')
    gst_number = models.CharField(max_length=15, blank=True, verbose_name='GST Number')
    pan_number = models.CharField(max_length=10, blank=True, verbose_name='PAN Number')
    contact_person = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    pincode = models.CharField(max_length=10, blank=True)
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    bank_name = models.CharField(max_length=150, blank=True)
    bank_account = models.CharField(max_length=30, blank=True)
    bank_ifsc = models.CharField(max_length=11, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = 'vendor'
        ordering = ['-created_at']
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
 
    def __str__(self):
        return f"{self.vendor_code} - {self.vendor_name}"
 
    def save(self, *args, **kwargs):
        if not self.vendor_code:
            last = Vendor.objects.order_by('-id').first()
            next_id = (last.id + 1) if last else 1
            self.vendor_code = f"VND-{next_id:04d}"
        super().save(*args, **kwargs)
 
    def get_status_badge(self):
        badges = {
            'active': 'success',
            'inactive': 'secondary',
            'blocked': 'danger',
            'pending': 'warning',
        }
        return badges.get(self.status, 'secondary')
 
    def get_rating_stars(self):
        return range(1, 6)
 
    @property
    def rating_percentage(self):
        return (self.rating / 5) * 100
 
 
class VendorDocument(models.Model):
    DOC_TYPES = [
        ('gst_cert', 'GST Certificate'),
        ('pan_card', 'PAN Card'),
        ('trade_license', 'Trade License'),
        ('bank_statement', 'Bank Statement'),
        ('other', 'Other'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=30, choices=DOC_TYPES)
    file = models.FileField(upload_to='vendor_docs/')
    name = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'vendor_document'
 
    def __str__(self):
        return f"{self.vendor.vendor_name} - {self.name}"
 
 
class VendorActivity(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=200)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)
 
    class Meta:
        db_table = 'vendor_activity'
        ordering = ['-created_at']
 
    def __str__(self):
        return f"{self.vendor.vendor_name} - {self.action}"