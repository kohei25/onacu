from django.urls import path

from . import views

app_name = 'cms'
urlpatterns = [
    path('', views.TopView.as_view(), name='top')
]