from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm

from .models import User, Event, Ticket

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
        self.fields['username'].help_text = 'この項目は必須です。150文字以下にしてください。例: オンアク太郎'
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data['email']
        User.objects.filter(email=email, is_active=False).delete()
        return email

class PwChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PwResetForm(PasswordResetForm):
    """パスワード忘れたときのフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class PwSetForm(SetPasswordForm):
    """パスワード再設定用フォーム(パスワード忘れて再設定)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class EventForm(forms.ModelForm):
  class Meta:
    model = Event
    fields = ("name", "date", "personal_time", "total_ticket", "image")

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
      field.widget.attrs['class'] = 'form-control'
    self.fields['date'].widget.attrs['class'] = 'form-control datetimepicker-input'
    self.fields['date'].widget.attrs['data-toggle'] = 'datetimepicker'
    self.fields['date'].widget.attrs['data-target'] = '#id_date'
    self.fields['date'].widget.attrs['readonly'] = 'readonly'
    self.fields['image'].widget.attrs['class'] = 'form-control-file'
    self.fields['personal_time'].widget.attrs['min'] = self.Meta.model.MIN_PERSONAL_TIME
    self.fields['personal_time'].widget.attrs['max'] = self.Meta.model.MAX_PERSONAL_TIME
    self.fields['total_ticket'].widget.attrs['min'] = self.Meta.model.MIN_TOTAL_TICKET
    self.fields['total_ticket'].widget.attrs['max'] = self.Meta.model.MAX_TOTAL_TICKET

class EventBuyForm(forms.ModelForm):
  class Meta:
    model = Ticket
    fields = ("event", )