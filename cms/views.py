from django.contrib.auth import get_user_model
from django.contrib.auth.views import (
    LoginView,
)
from django.views.generic.base import TemplateView

from .forms import (
    LoginForm,
)

UserModel = get_user_model()


class TopView(TemplateView):
    template_name = 'cms/top.html'


class Login(LoginView):
    form_class = LoginForm
    template_name = 'cms/login.html'