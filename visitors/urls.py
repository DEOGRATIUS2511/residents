from django.urls import path
from . import views

app_name = 'visitors'

urlpatterns = [
    path('log/', views.visitor_log, name='log'),
    path('register/', views.register_visitor, name='register'),
    path('exit/<int:pk>/', views.visitor_exit, name='exit'),
    path('detail/<int:pk>/', views.visitor_detail, name='detail'),
]
