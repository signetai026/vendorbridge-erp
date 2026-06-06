from django.shortcuts import render


def quotation_list(request):
    return render(request, 'quotations/quotation_list.html')


def quotation_create(request, rfq_pk=None):
    return render(request, 'quotations/create.html')


def quotation_detail(request, pk):
    return render(request, 'quotations/quotation_detail.html')