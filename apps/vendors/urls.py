from django.urls import path
from . import views
<<<<<<< Updated upstream

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
=======
 
app_name = 'vendors'
 
urlpatterns = [
    path('', views.vendor_dashboard, name='vendor_dashboard'),
    path('list/', views.vendor_list, name='vendor_list'),
>>>>>>> Stashed changes
    path('create/', views.vendor_create, name='vendor_create'),
    path('<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('<int:pk>/edit/', views.vendor_edit, name='vendor_edit'),
    path('<int:pk>/delete/', views.vendor_delete, name='vendor_delete'),
<<<<<<< Updated upstream
=======
    path('<int:pk>/toggle-status/', views.vendor_toggle_status, name='vendor_toggle_status'),
    path('<int:pk>/upload-doc/', views.vendor_upload_doc, name='vendor_upload_doc'),
    path('categories/', views.vendor_category_list, name='category_list'),
    path('categories/create/', views.vendor_category_create, name='category_create'),
    path('api/stats/', views.vendor_api_stats, name='api_stats'),
>>>>>>> Stashed changes
]