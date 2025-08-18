from django.urls import path
from . import views

app_name = 'residents'

urlpatterns = [
    path('', views.resident_list, name='list'),
    path('register/', views.resident_register, name='register'),
    path('profile/', views.resident_profile, name='profile'),
    path('profile/<int:pk>/', views.resident_detail, name='detail'),
    path('profile/<int:pk>/edit/', views.resident_edit, name='edit'),
]
