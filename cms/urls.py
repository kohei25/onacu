from django.urls import path

from . import views

app_name = 'cms'
urlpatterns = [
    path('', views.TopView.as_view(), name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('event/new/', views.EventCreateView.as_view(), name='eve_new'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='eve_de'),
    path('event/<int:event_id>/buy/', views.EventBuyView.as_view(), name='buy'),
]