from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('add_sale/', views.add_sale, name='add_sale'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('download/<str:filename>/', views.download_file, name='download_file'),
    path('delete/<str:filename>/', views.delete_file, name='delete_file'),
    path('delete_sale/<str:sale_id>/', views.delete_sale, name='delete_sale'),
    path('search_sales/', views.search_sales, name='search_sales'),
    path('edit_sale/<uuid:sale_id>/', views.edit_sale, name='edit_sale'),
    path('delete_db_sale/<uuid:sale_id>/', views.delete_db_sale, name='delete_db_sale'),
    path('edit_file_sale/<str:sale_id>/', views.edit_file_sale, name='edit_file_sale'),
]