from django.shortcuts import render, redirect
from .models import RFQ
from .forms import RFQForm


def rfq_list(request):
    rfqs = RFQ.objects.all().order_by('-id')

    return render(request, 'rfqs/rfq_list.html', {
        'rfqs': rfqs,
        'page_title': 'RFQ Management'
    })


def rfq_create(request):
    form = RFQForm()

    if request.method == "POST":
        form = RFQForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('/rfqs/')

    return render(request, 'rfqs/rfq_form.html', {
        'form': form
    })


def rfq_detail(request, pk):
    rfq = RFQ.objects.get(pk=pk)

    return render(request, 'rfqs/rfq_detail.html', {
        'rfq': rfq
    })


def rfq_edit(request, pk):
    rfq = RFQ.objects.get(pk=pk)

    if request.method == "POST":
        form = RFQForm(request.POST, instance=rfq)

        if form.is_valid():
            form.save()
            return redirect('/rfqs/')

    else:
        form = RFQForm(instance=rfq)

    return render(request, 'rfqs/rfq_form.html', {
        'form': form
    })


def rfq_publish(request, pk):
    return redirect('/rfqs/')


def rfq_cancel(request, pk):
    return redirect('/rfqs/')


def quotation_comparison(request, rfq_pk):
    return render(request, 'quotations/quotation_comparison.html')


def select_vendor(request, rfq_pk, quotation_pk):
    return redirect('/rfqs/')


def submit_for_approval(request, rfq_pk):
    return redirect('/rfqs/')