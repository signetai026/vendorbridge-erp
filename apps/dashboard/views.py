from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta, date
import json
 
from vendors.models import Vendor
from .models import RFQ, PurchaseOrder, Invoice, Approval
 
 
@login_required
def index(request):
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
 
    # Summary cards
    active_rfqs = RFQ.objects.filter(status__in=['sent', 'received']).count()
    pending_approvals = Approval.objects.filter(status='pending').count()
    pos_this_month = PurchaseOrder.objects.filter(created_at__date__gte=this_month_start).count()
    overdue_invoices = Invoice.objects.filter(status='overdue').count()
 
    # Recent data
    recent_rfqs = RFQ.objects.select_related('vendor', 'created_by').order_by('-created_at')[:5]
    recent_pos = PurchaseOrder.objects.select_related('vendor', 'created_by').order_by('-created_at')[:5]
    recent_invoices = Invoice.objects.select_related('vendor').order_by('-created_at')[:5]
    pending_approval_list = Approval.objects.filter(status='pending').select_related('requested_by').order_by('-created_at')[:5]
 
    # Monthly spend for chart (last 6 months)
    monthly_spend = []
    monthly_labels = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i * 30)
        month_start = month_date.replace(day=1)
        month_name = month_date.strftime('%b %Y')
        spend = PurchaseOrder.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lt=(month_start.replace(month=month_start.month % 12 + 1, day=1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1, day=1))
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        monthly_spend.append(float(spend))
        monthly_labels.append(month_name)
 
    # Vendor performance (top 5 by PO count)
    vendor_perf = Vendor.objects.annotate(
        po_count=Count('purchaseorder')
    ).order_by('-po_count')[:5]
    vendor_labels = [v.vendor_name[:15] for v in vendor_perf]
    vendor_data = [v.po_count for v in vendor_perf]
 
    # RFQ stats
    rfq_stats = {
        'draft': RFQ.objects.filter(status='draft').count(),
        'sent': RFQ.objects.filter(status='sent').count(),
        'received': RFQ.objects.filter(status='received').count(),
        'approved': RFQ.objects.filter(status='approved').count(),
        'rejected': RFQ.objects.filter(status='rejected').count(),
    }
 
    context = {
        'page_title': 'Dashboard',
        'active_rfqs': active_rfqs,
        'pending_approvals': pending_approvals,
        'pos_this_month': pos_this_month,
        'overdue_invoices': overdue_invoices,
        'recent_rfqs': recent_rfqs,
        'recent_pos': recent_pos,
        'recent_invoices': recent_invoices,
        'pending_approval_list': pending_approval_list,
        'monthly_spend_json': json.dumps(monthly_spend),
        'monthly_labels_json': json.dumps(monthly_labels),
        'vendor_labels_json': json.dumps(vendor_labels),
        'vendor_data_json': json.dumps(vendor_data),
        'rfq_stats_json': json.dumps(rfq_stats),
        'total_vendors': Vendor.objects.filter(status='active').count(),
        'total_po_value': PurchaseOrder.objects.filter(
            created_at__date__gte=this_month_start
        ).aggregate(total=Sum('grand_total'))['total'] or 0,
    }
    return render(request, 'dashboard/index.html', context)
 
 
@login_required
def rfq_list(request):
    rfqs = RFQ.objects.select_related('vendor', 'created_by').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status_filter:
        rfqs = rfqs.filter(status=status_filter)
    if q:
        rfqs = rfqs.filter(Q(rfq_number__icontains=q) | Q(title__icontains=q))
 
    from django.core.paginator import Paginator
    paginator = Paginator(rfqs, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
 
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'q': q,
        'page_title': 'RFQs',
        'status_choices': RFQ.STATUS_CHOICES,
    }
    return render(request, 'dashboard/rfq_list.html', context)
 
 
@login_required
def po_list(request):
    pos = PurchaseOrder.objects.select_related('vendor', 'created_by').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status_filter:
        pos = pos.filter(status=status_filter)
    if q:
        pos = pos.filter(Q(po_number__icontains=q) | Q(vendor__vendor_name__icontains=q))
 
    from django.core.paginator import Paginator
    paginator = Paginator(pos, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
 
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'q': q,
        'page_title': 'Purchase Orders',
        'status_choices': PurchaseOrder.STATUS_CHOICES,
    }
    return render(request, 'dashboard/po_list.html', context)
 
 
@login_required
def invoice_list(request):
    invoices = Invoice.objects.select_related('vendor', 'purchase_order').order_by('-created_at')
    status_filter = request.GET.get('status', '')
    q = request.GET.get('q', '')
    if status_filter:
        invoices = invoices.filter(status=status_filter)
    if q:
        invoices = invoices.filter(Q(invoice_number__icontains=q) | Q(vendor__vendor_name__icontains=q))
 
    from django.core.paginator import Paginator
    paginator = Paginator(invoices, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
 
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'q': q,
        'page_title': 'Invoices',
        'status_choices': Invoice.STATUS_CHOICES,
    }
    return render(request, 'dashboard/invoice_list.html', context)
 
 
@login_required
def approval_list(request):
    approvals = Approval.objects.select_related('requested_by', 'reviewed_by').order_by('-created_at')
    status_filter = request.GET.get('status', 'pending')
    if status_filter:
        approvals = approvals.filter(status=status_filter)
 
    from django.core.paginator import Paginator
    paginator = Paginator(approvals, 15)
    page_obj = paginator.get_page(request.GET.get('page'))
 
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'page_title': 'Approvals',
    }
    return render(request, 'dashboard/approval_list.html', context)
 
 
@login_required
def reports_view(request):
    today = timezone.now().date()
    this_month_start = today.replace(day=1)
 
    # Monthly spend last 12 months
    months_data = []
    for i in range(11, -1, -1):
        month_date = today - timedelta(days=i * 30)
        month_start = month_date.replace(day=1)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        spend = PurchaseOrder.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lt=month_end
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        months_data.append({
            'label': month_date.strftime('%b %Y'),
            'value': float(spend)
        })
 
    context = {
        'page_title': 'Reports',
        'months_data_json': json.dumps(months_data),
        'total_po_value': PurchaseOrder.objects.aggregate(t=Sum('grand_total'))['t'] or 0,
        'total_invoices_paid': Invoice.objects.filter(status='paid').aggregate(t=Sum('amount'))['t'] or 0,
        'total_vendors': Vendor.objects.count(),
        'total_rfqs': RFQ.objects.count(),
    }
    return render(request, 'dashboard/reports.html', context)
 
 
@login_required
def activity_view(request):
    from vendors.models import VendorActivity
    activities = VendorActivity.objects.select_related('vendor', 'performed_by').order_by('-created_at')
 
    from django.core.paginator import Paginator
    paginator = Paginator(activities, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
 
    return render(request, 'dashboard/activity.html', {
        'page_obj': page_obj, 'page_title': 'Activity Log'
    })