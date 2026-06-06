from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),

    path('rfqs/', views.rfq_list, name='rfq_list'),
    path('purchase-orders/', views.po_list, name='po_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('approvals/', views.approval_list, name='approval_list'),
    path('reports/', views.reports_view, name='reports'),
    path('activity/', views.activity_view, name='activity'),
]