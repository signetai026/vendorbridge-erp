from django.shortcuts import render

def purchase_order_list(request):
    return render(request, 'purchase_orders/po_list.html')