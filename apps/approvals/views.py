from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import Vendor, RFQ, RFQItem, Quotation, QuotationItem, ApprovalWorkflow, ApprovalAction
from .forms import VendorForm, RFQForm, RFQItemFormSet, QuotationForm, QuotationItemFormSet
from activity.models import ActivityLog
from purchase_orders.models import PurchaseOrder, POItem


# ============ VENDOR VIEWS ============

@login_required
def vendor_list(request):
    vendors = Vendor.objects.all()
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')

    if search:
        vendors = vendors.filter(
            Q(company_name__icontains=search) |
            Q(contact_person__icontains=search) |
            Q(email__icontains=search) |
            Q(gst_number__icontains=search)
        )
    if category:
        vendors = vendors.filter(category=category)
    if status:
        vendors = vendors.filter(status=status)

    paginator = Paginator(vendors, 15)
    page = request.GET.get('page', 1)
    vendors_page = paginator.get_page(page)

    stats = {
        'total': Vendor.objects.count(),
        'active': Vendor.objects.filter(status='active').count(),
        'inactive': Vendor.objects.filter(status='inactive').count(),
        'blacklisted': Vendor.objects.filter(status='blacklisted').count(),
    }

    return render(request, 'vendors/vendor_list.html', {
        'vendors': vendors_page,
        'stats': stats,
        'search': search,
        'category': category,
        'status': status,
        'category_choices': Vendor.CATEGORY_CHOICES,
    })


@login_required
def vendor_create(request):
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.created_by = request.user
            vendor.save()
            ActivityLog.log(request.user, 'vendor_created', f'Vendor {vendor.company_name} created', vendor, request)
            messages.success(request, f'Vendor "{vendor.company_name}" created successfully.')
            return redirect('vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm()
    return render(request, 'vendors/vendor_form.html', {'form': form, 'title': 'Add New Vendor'})


@login_required
def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    pos = PurchaseOrder.objects.filter(vendor=vendor).order_by('-created_at')[:5]
    quotations = Quotation.objects.filter(vendor=vendor).select_related('rfq').order_by('-submitted_at')[:5]
    rfqs = vendor.rfqs.order_by('-created_at')[:5]

    po_total = PurchaseOrder.objects.filter(
        vendor=vendor, status__in=['approved', 'issued', 'completed']
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    return render(request, 'vendors/vendor_detail.html', {
        'vendor': vendor,
        'pos': pos,
        'quotations': quotations,
        'rfqs': rfqs,
        'po_total': po_total,
    })


@login_required
def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            ActivityLog.log(request.user, 'vendor_updated', f'Vendor {vendor.company_name} updated', vendor, request)
            messages.success(request, 'Vendor updated successfully.')
            return redirect('vendor_detail', pk=vendor.pk)
    else:
        form = VendorForm(instance=vendor)
    return render(request, 'vendors/vendor_form.html', {'form': form, 'vendor': vendor, 'title': 'Edit Vendor'})


@login_required
def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == 'POST':
        name = vendor.company_name
        vendor.is_active = False
        vendor.status = 'inactive'
        vendor.save()
        ActivityLog.log(request.user, 'vendor_deleted', f'Vendor {name} deactivated', vendor, request)
        messages.success(request, f'Vendor "{name}" deactivated.')
        return redirect('vendor_list')
    return render(request, 'vendors/vendor_confirm_delete.html', {'vendor': vendor})


# ============ RFQ VIEWS ============

@login_required
def rfq_list(request):
    rfqs = RFQ.objects.select_related('created_by').all()
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')

    if search:
        rfqs = rfqs.filter(Q(rfq_number__icontains=search) | Q(title__icontains=search))
    if status:
        rfqs = rfqs.filter(status=status)
    if priority:
        rfqs = rfqs.filter(priority=priority)

    paginator = Paginator(rfqs, 15)
    page = request.GET.get('page', 1)
    rfqs_page = paginator.get_page(page)

    stats = {
        'total': RFQ.objects.count(),
        'draft': RFQ.objects.filter(status='draft').count(),
        'published': RFQ.objects.filter(status='published').count(),
        'evaluation': RFQ.objects.filter(status='evaluation').count(),
        'awarded': RFQ.objects.filter(status='awarded').count(),
    }
    return render(request, 'rfq/rfq_list.html', {
        'rfqs': rfqs_page, 'stats': stats,
        'search': search, 'status': status, 'priority': priority,
    })


@login_required
def rfq_create(request):
    if request.method == 'POST':
        form = RFQForm(request.POST)
        formset = RFQItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            rfq = form.save(commit=False)
            rfq.created_by = request.user
            rfq.save()
            form.save_m2m()
            formset.instance = rfq
            formset.save()
            ActivityLog.log(request.user, 'rfq_created', f'RFQ {rfq.rfq_number} created', rfq, request)
            messages.success(request, f'RFQ "{rfq.rfq_number}" created successfully.')
            return redirect('rfq_detail', pk=rfq.pk)
    else:
        form = RFQForm()
        formset = RFQItemFormSet(prefix='items')
    return render(request, 'rfq/rfq_form.html', {'form': form, 'formset': formset, 'title': 'Create RFQ'})


@login_required
def rfq_detail(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)
    quotations = rfq.quotations.select_related('vendor').all()
    return render(request, 'rfq/rfq_detail.html', {
        'rfq': rfq,
        'quotations': quotations,
        'items': rfq.items.all(),
    })


@login_required
def rfq_edit(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)
    if rfq.status not in ['draft']:
        messages.warning(request, 'Only draft RFQs can be edited.')
        return redirect('rfq_detail', pk=rfq.pk)
    if request.method == 'POST':
        form = RFQForm(request.POST, instance=rfq)
        formset = RFQItemFormSet(request.POST, instance=rfq, prefix='items')
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'RFQ updated successfully.')
            return redirect('rfq_detail', pk=rfq.pk)
    else:
        form = RFQForm(instance=rfq)
        formset = RFQItemFormSet(instance=rfq, prefix='items')
    return render(request, 'rfq/rfq_form.html', {'form': form, 'formset': formset, 'rfq': rfq, 'title': 'Edit RFQ'})


@login_required
def rfq_publish(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)
    if rfq.status == 'draft':
        rfq.status = 'published'
        rfq.published_at = timezone.now()
        rfq.save()
        ActivityLog.log(request.user, 'rfq_published', f'RFQ {rfq.rfq_number} published', rfq, request)
        # Send emails to invited vendors
        for vendor in rfq.vendors.all():
            try:
                send_mail(
                    subject=f'RFQ Assignment: {rfq.rfq_number} - {rfq.title}',
                    message=f'Dear {vendor.contact_person},\n\nYou have been invited to submit a quotation for:\nRFQ: {rfq.rfq_number}\nTitle: {rfq.title}\nDeadline: {rfq.deadline}\n\nPlease login to VendorBridge ERP to submit your quotation.\n\nRegards,\nVendorBridge ERP Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[vendor.email],
                    fail_silently=True,
                )
            except Exception:
                pass
        messages.success(request, f'RFQ published and vendors notified.')
    return redirect('rfq_detail', pk=rfq.pk)


@login_required
def rfq_cancel(request, pk):
    rfq = get_object_or_404(RFQ, pk=pk)
    if request.method == 'POST':
        rfq.status = 'cancelled'
        rfq.save()
        ActivityLog.log(request.user, 'rfq_cancelled', f'RFQ {rfq.rfq_number} cancelled', rfq, request)
        messages.success(request, 'RFQ cancelled.')
    return redirect('rfq_detail', pk=rfq.pk)


# ============ QUOTATION VIEWS ============

@login_required
def quotation_list(request):
    quotations = Quotation.objects.select_related('vendor', 'rfq').all()
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')

    if search:
        quotations = quotations.filter(
            Q(quotation_number__icontains=search) |
            Q(vendor__company_name__icontains=search) |
            Q(rfq__rfq_number__icontains=search)
        )
    if status:
        quotations = quotations.filter(status=status)

    paginator = Paginator(quotations, 15)
    page = request.GET.get('page', 1)
    return render(request, 'quotations/quotation_list.html', {
        'quotations': paginator.get_page(page),
        'search': search, 'status': status,
    })


@login_required
def quotation_create(request, rfq_pk=None):
    rfq = get_object_or_404(RFQ, pk=rfq_pk) if rfq_pk else None
    if request.method == 'POST':
        form = QuotationForm(request.POST)
        formset = QuotationItemFormSet(request.POST, prefix='items')
        if form.is_valid() and formset.is_valid():
            quotation = form.save(commit=False)
            # Calculate totals from items
            items = formset.save(commit=False)
            subtotal = sum(item.total_price for item in items)
            quotation.subtotal = subtotal
            quotation.save()
            for item in items:
                item.quotation = quotation
                item.save()
            ActivityLog.log(request.user, 'quotation_submitted', f'Quotation {quotation.quotation_number} submitted', quotation, request)
            messages.success(request, f'Quotation {quotation.quotation_number} submitted successfully.')
            return redirect('quotation_detail', pk=quotation.pk)
    else:
        initial = {}
        if rfq:
            initial['rfq'] = rfq
        form = QuotationForm(initial=initial)
        formset = QuotationItemFormSet(prefix='items')
    return render(request, 'quotations/quotation_form.html', {
        'form': form, 'formset': formset, 'rfq': rfq, 'title': 'Submit Quotation',
    })


@login_required
def quotation_detail(request, pk):
    quotation = get_object_or_404(Quotation, pk=pk)
    return render(request, 'quotations/quotation_detail.html', {'quotation': quotation})


@login_required
def quotation_comparison(request, rfq_pk):
    rfq = get_object_or_404(RFQ, pk=rfq_pk)
    quotations = rfq.quotations.select_related('vendor').filter(
        status__in=['submitted', 'under_review', 'shortlisted', 'selected']
    )

    if not quotations.exists():
        messages.warning(request, 'No quotations available for comparison.')
        return redirect('rfq_detail', pk=rfq_pk)

    # Sort logic
    sort_by = request.GET.get('sort', 'price')
    if sort_by == 'delivery':
        quotations = quotations.order_by('delivery_days')
    elif sort_by == 'rating':
        quotations = quotations.order_by('-vendor__rating')
    else:
        quotations = quotations.order_by('grand_total')

    # Identify best values
    min_price = quotations.order_by('grand_total').first()
    min_delivery = quotations.order_by('delivery_days').first()
    max_rating = quotations.order_by('-vendor__rating').first()

    # Best vendor recommendation scoring
    def score_vendor(q):
        price_score = 0
        if min_price and min_price.grand_total > 0:
            price_score = (1 - (float(q.grand_total - min_price.grand_total) / float(min_price.grand_total + 1))) * 40
        delivery_score = max(0, (30 - q.delivery_days) / 30 * 30)
        rating_score = float(q.vendor.rating) / 5 * 30
        return price_score + delivery_score + rating_score

    scored = [(q, score_vendor(q)) for q in quotations]
    scored.sort(key=lambda x: x[1], reverse=True)
    best_vendor = scored[0][0] if scored else None

    ActivityLog.log(request.user, 'comparison_viewed', f'Quotation comparison viewed for RFQ {rfq.rfq_number}', rfq, request)

    return render(request, 'quotations/quotation_comparison.html', {
        'rfq': rfq,
        'quotations': quotations,
        'scored': scored,
        'min_price': min_price,
        'min_delivery': min_delivery,
        'max_rating': max_rating,
        'best_vendor': best_vendor,
        'sort_by': sort_by,
        'items': rfq.items.all(),
    })


@login_required
def select_vendor(request, rfq_pk, quotation_pk):
    rfq = get_object_or_404(RFQ, pk=rfq_pk)
    quotation = get_object_or_404(Quotation, pk=quotation_pk, rfq=rfq)

    if request.method == 'POST':
        # Deselect all others
        rfq.quotations.update(is_selected=False, status='under_review')
        quotation.is_selected = True
        quotation.status = 'selected'
        quotation.save()
        rfq.status = 'evaluation'
        rfq.save()
        ActivityLog.log(request.user, 'vendor_selected', f'Vendor {quotation.vendor.company_name} selected for RFQ {rfq.rfq_number}', quotation, request)
        messages.success(request, f'Vendor {quotation.vendor.company_name} selected. You can now proceed with approval.')
        return redirect('quotation_comparison', rfq_pk=rfq_pk)
    return redirect('quotation_comparison', rfq_pk=rfq_pk)


@login_required
def submit_for_approval(request, rfq_pk):
    rfq = get_object_or_404(RFQ, pk=rfq_pk)
    selected_quotation = rfq.quotations.filter(is_selected=True).first()

    if not selected_quotation:
        messages.error(request, 'Please select a vendor quotation first.')
        return redirect('quotation_comparison', rfq_pk=rfq_pk)

    # Check if workflow already exists
    existing = ApprovalWorkflow.objects.filter(rfq=rfq, is_active=True).first()
    if existing:
        messages.info(request, 'Approval workflow already exists.')
        return redirect('approval_detail', pk=existing.pk)

    workflow = ApprovalWorkflow.objects.create(
        rfq=rfq,
        quotation=selected_quotation,
        current_stage='submitted',
        created_by=request.user,
    )
    ApprovalAction.objects.create(
        workflow=workflow,
        stage='submitted',
        action='submitted',
        acted_by=request.user,
        comments=f'Submitted for approval. Selected vendor: {selected_quotation.vendor.company_name}'
    )
    ActivityLog.log(request.user, 'approval_submitted', f'RFQ {rfq.rfq_number} submitted for approval', rfq, request)
    messages.success(request, 'Submitted for approval workflow.')
    return redirect('approval_detail', pk=workflow.pk)


# ============ APPROVAL WORKFLOW VIEWS ============

@login_required
def approval_list(request):
    workflows = ApprovalWorkflow.objects.select_related('rfq', 'quotation__vendor', 'created_by').filter(is_active=True)
    stage = request.GET.get('stage', '')
    if stage:
        workflows = workflows.filter(current_stage=stage)

    paginator = Paginator(workflows, 15)
    page = request.GET.get('page', 1)

    stats = {
        'submitted': ApprovalWorkflow.objects.filter(current_stage='submitted', is_active=True).count(),
        'l1': ApprovalWorkflow.objects.filter(current_stage='l1_review', is_active=True).count(),
        'l2': ApprovalWorkflow.objects.filter(current_stage='l2_approval', is_active=True).count(),
        'approved': ApprovalWorkflow.objects.filter(current_stage='approved', is_active=True).count(),
        'rejected': ApprovalWorkflow.objects.filter(current_stage='rejected', is_active=True).count(),
    }

    return render(request, 'approvals/approval_list.html', {
        'workflows': paginator.get_page(page),
        'stats': stats, 'stage': stage,
    })


@login_required
def approval_detail(request, pk):
    workflow = get_object_or_404(ApprovalWorkflow, pk=pk)
    actions = workflow.actions.select_related('acted_by').all()
    return render(request, 'approvals/approval_detail.html', {
        'workflow': workflow,
        'actions': actions,
        'quotation': workflow.quotation,
        'rfq': workflow.rfq,
    })


@login_required
def approval_action(request, pk):
    workflow = get_object_or_404(ApprovalWorkflow, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        comments = request.POST.get('comments', '')

        stage_progression = {
            'submitted': 'l1_review',
            'l1_review': 'l2_approval',
            'l2_approval': 'procurement_head',
            'procurement_head': 'generate_po',
        }

        if action == 'approve':
            next_stage = stage_progression.get(workflow.current_stage)
            if next_stage:
                ApprovalAction.objects.create(
                    workflow=workflow,
                    stage=workflow.current_stage,
                    action='approved',
                    acted_by=request.user,
                    comments=comments
                )
                workflow.current_stage = next_stage
                workflow.save()
                ActivityLog.log(request.user, 'approval_approved', f'Workflow approved at {workflow.current_stage}', workflow, request)

                if next_stage == 'generate_po':
                    workflow.current_stage = 'approved'
                    workflow.save()
                    messages.success(request, 'Final approval granted. You can now generate the Purchase Order.')
                else:
                    messages.success(request, f'Approved and moved to {workflow.get_current_stage_display()}.')
            else:
                messages.error(request, 'Cannot advance workflow further.')

        elif action == 'reject':
            ApprovalAction.objects.create(
                workflow=workflow,
                stage=workflow.current_stage,
                action='rejected',
                acted_by=request.user,
                comments=comments
            )
            workflow.current_stage = 'rejected'
            workflow.save()
            workflow.rfq.status = 'closed'
            workflow.rfq.save()
            ActivityLog.log(request.user, 'approval_rejected', f'Workflow rejected at {workflow.current_stage}', workflow, request)
            messages.warning(request, 'Workflow rejected.')

        return redirect('approval_detail', pk=workflow.pk)

    return redirect('approval_detail', pk=workflow.pk)


@login_required
def generate_po_from_workflow(request, pk):
    workflow = get_object_or_404(ApprovalWorkflow, pk=pk)

    if workflow.current_stage != 'approved':
        messages.error(request, 'Workflow must be fully approved before generating PO.')
        return redirect('approval_detail', pk=pk)

    quotation = workflow.quotation
    rfq = workflow.rfq

    # Check if PO already exists
    existing_po = PurchaseOrder.objects.filter(quotation=quotation).first()
    if existing_po:
        messages.info(request, f'PO {existing_po.po_number} already exists.')
        return redirect('po_detail', pk=existing_po.pk)

    po = PurchaseOrder.objects.create(
        vendor=quotation.vendor,
        rfq=rfq,
        quotation=quotation,
        status='approved',
        delivery_address=rfq.delivery_address or '',
        delivery_date=rfq.delivery_date,
        payment_terms=quotation.get_payment_terms_display(),
        subtotal=quotation.subtotal,
        gst_amount=quotation.gst_amount,
        discount_amount=quotation.discount_amount,
        total_amount=quotation.grand_total,
        created_by=request.user,
        approved_by=request.user,
        approved_at=timezone.now(),
    )

    # Copy items from quotation
    for q_item in quotation.items.all():
        POItem.objects.create(
            purchase_order=po,
            item_name=q_item.item_name,
            description=q_item.description,
            quantity=q_item.quantity,
            unit=q_item.unit,
            unit_price=q_item.unit_price,
            total_price=q_item.total_price,
        )

    rfq.status = 'awarded'
    rfq.save()
    workflow.current_stage = 'generate_po'
    workflow.is_active = False
    workflow.save()

    ActivityLog.log(request.user, 'po_generated', f'PO {po.po_number} generated from workflow', po, request)
    messages.success(request, f'Purchase Order {po.po_number} generated successfully.')
    return redirect('po_detail', pk=po.pk)