from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
    path('detail/', views.detail, name='detail'),
    path('export/', views.export_view, name='export'),
]