from django.urls import path
from . import views

urlpatterns = [
    path('', views.rfq_list, name='rfq_list'),
    path('create/', views.rfq_create, name='rfq_create'),
    path('<int:pk>/', views.rfq_detail, name='rfq_detail'),
    path('<int:pk>/edit/', views.rfq_edit, name='rfq_edit'),
    path('<int:pk>/publish/', views.rfq_publish, name='rfq_publish'),
    path('<int:pk>/cancel/', views.rfq_cancel, name='rfq_cancel'),
    path('<int:rfq_pk>/compare/', views.quotation_comparison, name='quotation_comparison'),
    path('<int:rfq_pk>/select/<int:quotation_pk>/', views.select_vendor, name='select_vendor'),
    path('<int:rfq_pk>/submit-approval/', views.submit_for_approval, name='submit_for_approval'),
]