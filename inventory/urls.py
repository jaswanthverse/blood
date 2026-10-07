from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.unit_list, name='unit_list'),
    path('add/', views.unit_add, name='unit_add'),
    path('<int:pk>/', views.unit_detail, name='unit_detail'),
    path('<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    path('<int:pk>/reserve/', views.unit_reserve, name='unit_reserve'),
    path('<int:pk>/release/', views.unit_release, name='unit_release'),
    path('<int:pk>/issue/', views.unit_issue, name='unit_issue'),
]