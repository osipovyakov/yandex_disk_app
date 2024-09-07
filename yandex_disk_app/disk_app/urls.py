from django.urls import path
from . import views


app_name = 'disk_app'


urlpatterns = [
    path('', views.start_page, name='start_page'),
    path('file_list/', views.file_list, name='file_list'),
    path('download/<path:file_path>/', views.download_file, name='download_file'),
    path('download-multiple/', views.download_multiple_files, name='download_multiple_files'),
]