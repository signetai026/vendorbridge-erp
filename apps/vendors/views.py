from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
 
from .models import Vendor, VendorCategory, VendorActivity, VendorDocument
from .forms import VendorForm, VendorCategoryForm, VendorFilterForm, VendorDocumentForm
from accounts.decorators import procurement_access_required
 
 
def log_activity(vendor, action, user, details=''):
    VendorActivity.objects.create(vendor=vendor, action=action, performed_by=user, details=details)
 
 
@login_required
def vendor_dashboard(request):
    total_vendors = Vendor.objects.count()
    active_vendors = Vendor.objects.filter(status='active').count()
    blocked_vendors = Vendor.objects.filter(status='blocked').count()
    pending_vendors = Vendor.objects.filter(status='pending').count()
    inactive_vendors = Vendor.objects.filter(status='inactive').count()
 
    category_stats = VendorCategory.objects.annotate(vendor_count=Count('vendors')).order_by('-vendor_count')[:8]
    recent_vendors = Vendor.objects.select_related('category').order_by('-created_at')[:5]
 
    rating_dist = {}
    for i in range(1, 6):
        rating_dist[i] = Vendor.objects.filter(rating=i).count()
 
    context = {
        'total_vendors': total_vendors,
        'active_vendors': active_vendors,
        'blocked_vendors': blocked_vendors,
        'pending_vendors': pending_vendors,
        'inactive_vendors': inactive_vendors,
        'category_stats': category_stats,
        'recent_vendors': recent_vendors,
        'rating_dist': rating_dist,
        'page_title': 'Vendor Dashboard',
    }
    return render(request, 'vendors/dashboard.html', context)
 
 
@login_required
def vendor_list(request):
    form = VendorFilterForm(request.GET)
    vendors = Vendor.objects.select_related('category').all()
 
    q = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    rating = request.GET.get('rating', '')
    city = request.GET.get('city', '')
 
    if q:
        vendors = vendors.filter(
            Q(vendor_name__icontains=q) |
            Q(company_name__icontains=q) |
            Q(email__icontains=q) |
            Q(vendor_code__icontains=q) |
            Q(contact_person__icontains=q) |
            Q(city__icontains=q)
        )
    if category_id:
        vendors = vendors.filter(category_id=category_id)
    if status:
        vendors = vendors.filter(status=status)
    if rating:
        vendors = vendors.filter(rating=int(rating))
    if city:
        vendors = vendors.filter(city__icontains=city)
 
    paginator = Paginator(vendors, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
 
    context = {
        'page_obj': page_obj,
        'form': form,
        'q': q,
        'total_count': vendors.count(),
        'page_title': 'Vendors',
    }
    return render(request, 'vendors/vendor_list.html', context)
 
 
@login_required
def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    activities = vendor.activities.select_related('performed_by').all()[:10]
    documents = vendor.documents.all()
    doc_form = VendorDocumentForm()
 
    context = {
        'vendor': vendor,
        'activities': activities,
        'documents': documents,
        'doc_form': doc_form,
        'page_title': vendor.vendor_name,
    }
    return render(request, 'vendors/vendor_detail.html', context)
 
 
@login_required
@procurement_access_required
def vendor_create(request):
    form = VendorForm()
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save()
            log_activity(vendor, 'Vendor Created', request.user, f'Created by {request.user.name}')
            messages.success(request, f'Vendor {vendor.vendor_name} created successfully!')
            return redirect('vendors:vendor_detail', pk=vendor.pk)
    return render(request, 'vendors/vendor_form.html', {
        'form': form, 'title': 'Add New Vendor', 'page_title': 'Add Vendor'
    })
 
 
@login_required
@procurement_access_required
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    form = VendorForm(instance=vendor)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            vendor = form.save()
            log_activity(vendor, 'Vendor Updated', request.user, f'Updated by {request.user.name}')
            messages.success(request, f'Vendor {vendor.vendor_name} updated successfully!')
            return redirect('vendors:vendor_detail', pk=vendor.pk)
    return render(request, 'vendors/vendor_form.html', {
        'form': form, 'title': f'Edit {vendor.vendor_name}', 'vendor': vendor, 'page_title': 'Edit Vendor'
    })
 
 
@login_required
@procurement_access_required
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        name = vendor.vendor_name
        vendor.delete()
        messages.success(request, f'Vendor {name} deleted successfully.')
        return redirect('vendors:vendor_list')
    return render(request, 'vendors/vendor_confirm_delete.html', {'vendor': vendor})
 
 
@login_required
@procurement_access_required
@require_POST
def vendor_toggle_status(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    new_status = request.POST.get('status', 'active')
    old_status = vendor.status
    vendor.status = new_status
    vendor.save()
    log_activity(vendor, f'Status Changed', request.user, f'{old_status} → {new_status}')
    messages.success(request, f'Vendor status updated to {vendor.get_status_display()}.')
    return redirect('vendors:vendor_detail', pk=vendor.pk)
 
 
@login_required
@procurement_access_required
def vendor_upload_doc(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.vendor = vendor
            doc.save()
            log_activity(vendor, 'Document Uploaded', request.user, f'Uploaded: {doc.name}')
            messages.success(request, 'Document uploaded successfully.')
    return redirect('vendors:vendor_detail', pk=vendor.pk)
 
 
@login_required
def vendor_category_list(request):
    categories = VendorCategory.objects.annotate(vendor_count=Count('vendors'))
    return render(request, 'vendors/category_list.html', {
        'categories': categories, 'page_title': 'Vendor Categories'
    })
 
 
@login_required
@procurement_access_required
def vendor_category_create(request):
    form = VendorCategoryForm()
    if request.method == 'POST':
        form = VendorCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created.')
            return redirect('vendors:category_list')
    return render(request, 'vendors/category_form.html', {'form': form, 'title': 'Add Category'})
 
 
@login_required
def vendor_api_stats(request):
    data = {
        'total': Vendor.objects.count(),
        'active': Vendor.objects.filter(status='active').count(),
        'blocked': Vendor.objects.filter(status='blocked').count(),
        'pending': Vendor.objects.filter(status='pending').count(),
        'by_category': list(
            VendorCategory.objects.annotate(count=Count('vendors')).values('name', 'count')
        ),
        'by_rating': [
            {'rating': i, 'count': Vendor.objects.filter(rating=i).count()} for i in range(1, 6)
        ],
    }
    return JsonResponse(data)