from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Event, Ticket

UserModel = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields['username'].widget.attrs['class'] = 'form-control'
       self.fields['password'].widget.attrs['class'] = 'form-control'

class UserCreateForm(UserCreationForm):
    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class EventForm(forms.ModelForm):
  class Meta:
    model = Event
    fields = ("name", "date", "personal_time", "total_ticket")

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs['class'] = 'form-control'
    self.fields['date'].widget.attrs['class'] = 'form-control datetimepicker-input'
    self.fields['date'].widget.attrs['data-toggle'] = 'datetimepicker'
    self.fields['date'].widget.attrs['data-target'] = '#id_date'

class EventBuyForm(forms.ModelForm):
  class Meta:
    model = Ticket
    fields = ("event", )