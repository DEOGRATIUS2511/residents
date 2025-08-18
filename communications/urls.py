from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('announcements/', views.announcements, name='announcements'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/<int:pk>/delete/', views.delete_announcement, name='delete_announcement'),
    path('complaints/', views.complaints, name='complaints'),
    path('complaints/create/', views.create_complaint, name='create_complaint'),
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<int:pk>/respond/', views.respond_complaint, name='respond_complaint'),
]
