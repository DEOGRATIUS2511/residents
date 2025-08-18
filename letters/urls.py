from django.urls import path
from . import views

app_name = 'letters'

urlpatterns = [
    path('request/', views.letter_request, name='request'),
    path('my-requests/', views.my_requests, name='my_requests'),
    path('pending/', views.pending_requests, name='pending'),
    path('all/', views.all_requests, name='all'),
    path('detail/<int:pk>/', views.request_detail, name='detail'),
    path('approve/<int:pk>/', views.approve_request, name='approve'),
    path('reject/<int:pk>/', views.reject_request, name='reject'),
    path('generate-pdf/<int:pk>/', views.generate_pdf, name='generate_pdf'),
]
