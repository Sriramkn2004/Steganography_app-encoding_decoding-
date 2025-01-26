from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('encode/', views.encode_image, name='encode'),
    path('decode/', views.decode_image, name='decode'),
]
