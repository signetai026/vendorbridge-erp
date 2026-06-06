from django.urls import path
from . import views

urlpatterns = [
    path('', views.approval_list, name='approval_list'),
    path('<int:pk>/', views.approval_detail, name='approval_detail'),
    path('<int:pk>/action/', views.approval_action, name='approval_action'),
    path('<int:pk>/generate-po/', views.generate_po_from_workflow, name='generate_po_from_workflow'),
]