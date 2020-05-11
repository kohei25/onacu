from django.urls import path

from . import views
from .views import EventCreateView

app_name = 'cms'
urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('event/new/', views.EventCreateView.as_view(), name='eve_new'),
]