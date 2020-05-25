from django.urls import path

from . import views

app_name = 'cms'
urlpatterns = [
    path('', views.topView, name='top'),
    path('top/', views.Top1View.as_view(), name='top1'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('event/new/', views.EventCreateView.as_view(), name='eve_new'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='eve_de'),
    path('event/<int:event_id>/buy/', views.eventBuyView, name='buy'),
    path('event/buy/after', views.ticketBuyAfter, name='buy_after'),
    path('event/<int:pk>/now/', views.event_now, name='eve_now'),
    path('event/<int:pk>/finish/', views.event_finish, name='eve_fin'),
    path('ajax/ticket/get/', views.ticketGet, name='ticket_info'),
    path('ajax/ticket/post/', views.ticketPost, name='update_ticket'),
]