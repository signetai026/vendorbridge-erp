from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Vendor
 
 
@receiver(post_save, sender=Vendor)
def vendor_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"[SIGNAL] New vendor created: {instance.vendor_code} - {instance.vendor_name}")
 
 
@receiver(pre_delete, sender=Vendor)
def vendor_pre_delete(sender, instance, **kwargs):
    print(f"[SIGNAL] Vendor being deleted: {instance.vendor_code} - {instance.vendor_name}")