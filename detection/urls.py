from django.urls import path
from . import views
from .views import chat_view

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/image/', views.upload_image, name='upload_image'),
    path('upload/video/', views.upload_video, name='upload_video'),
    path('detect_camera/', views.detect_fire_camera, name='detect_camera'),
    path('detect-fire-camera/', views.detect_fire_camera, name='detect_fire_camera'),
    path('detect/upload/', views.detect_file_upload, name='detect_file_upload'),
    path('history/', views.history, name='history_page'),
    path('history/delete/<int:id>/', views.delete_history, name='delete_history'),
    path('delete-all/', views.delete_all_history, name='delete_all'),
    path('delete-selected/', views.delete_selected_history, name='delete_selected'),
    path("chat/", chat_view, name="chat"),
]
