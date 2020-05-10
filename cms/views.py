from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import (
    LoginView, LogoutView,
)
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import (
    CreateView,
)

from .forms import (
    LoginForm, UserCreateForm,
)
UserModel = get_user_model()


class TopView(TemplateView):
    template_name = 'cms/top.html'


class Login(LoginView):
    form_class = LoginForm
    template_name = 'cms/login.html'

class Logout(LogoutView):
    pass

class UserCreate(CreateView):
    form_class = UserCreateForm
    template_name = 'cms/signup.html'
    success_url = reverse_lazy('cms:top')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.object = user
        return HttpResponseRedirect(self.get_success_url())