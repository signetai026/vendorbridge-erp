from django.shortcuts import render

def invoice_list(request):
    return render(request, 'invoices/invoice_list.html')