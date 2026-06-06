from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('vendors/', include('apps.vendors.urls')),

    path('rfqs/', include('apps.rfqs.urls')),
    path('quotations/', include('apps.quotations.urls')),
    path('approvals/', include('apps.approvals.urls')),
    path('purchase-orders/', include('apps.purchase_orders.urls')),
    path('invoices/', include('apps.invoices.urls')),
    path('reports/', include('apps.reports.urls')),
    path('activity-logs/', include('apps.activity_logs.urls')),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)