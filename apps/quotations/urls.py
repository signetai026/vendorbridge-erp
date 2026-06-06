from django.urls import path
from . import views

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    path('create/', views.quotation_create, name='quotation_create'),
    path('create/<int:rfq_pk>/', views.quotation_create, name='quotation_create_for_rfq'),
    path('<int:pk>/', views.quotation_detail, name='quotation_detail'),
]