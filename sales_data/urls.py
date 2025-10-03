from django.urls import path
from . import views

"""URL-паттерны для приложения данных о продажах"""
urlpatterns = [
    path('', views.index, name='index'),
    path('add_sale/', views.add_sale, name='add_sale'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
    path('delete/<str:filename>/', views.delete_file, name='delete_file'),
    path('delete_sale/<str:sale_id>/', views.delete_sale, name='delete_sale'),
]