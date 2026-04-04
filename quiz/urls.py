from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('countries/', views.country_list, name='country_list'),
    path('add/', views.add_country, name='add_country'),
    path('quiz/', views.quiz, name='quiz'),
    path('delete/<str:country_name>/', views.delete_country, name='delete_country')
]