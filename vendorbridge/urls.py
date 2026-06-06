from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('apps.accounts.urls')),
    path('', include('apps.dashboard.urls')),
    path('', include('apps.vendors.urls')),
    path('', include('apps.rfqs.urls')),
    path('', include('apps.quotations.urls')),
    path('', include('apps.approvals.urls')),
    path('', include('apps.purchase_orders.urls')),
    path('', include('apps.invoices.urls')),
    path('', include('apps.reports.urls')),
    path('', include('apps.activity_logs.urls')),
]