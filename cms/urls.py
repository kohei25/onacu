from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'cms'
urlpatterns = [
    path('', views.topView, name='top'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('signup/done', views.UserCreateDone.as_view(), name='signup_done'),
    path('signup/complete/<token>/', views.UserCreateComplete.as_view(), name='signup_complete'),
    path('mypage/', views.myPageView, name='mypage'),
    path('password/change/', views.PasswordChange.as_view(), name='password_change'),
    path('password/change/done', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('password/reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password/reset/done', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password/reset/complete', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('point/buy/', views.pointBuy, name='point_buy'),
    path('event/new/', login_required(views.EventCreateView.as_view()), name='eve_new'),
    path('event/<int:pk>/', views.eventDetail, name='eve_de'),
    path('event/<int:event_id>/buy/', views.eventBuyView, name='buy'),
    path('event/<int:event_id>/buy/after', views.ticketBuyAfter, name='buy_after'),
    path('event/<int:pk>/ical', views.event_ical, name='eve_ical'),
    path('event/<int:pk>/now/', views.event_now, name='eve_now'),
    path('event/<int:pk>/finish/', views.event_finish, name='eve_fin'),
    path('ajax/ticket/get/', views.ticketGet, name='ticket_info'),
    path('ajax/ticket/post/', views.ticketPost, name='update_ticket'),
]