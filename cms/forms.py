from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

UserModel = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.fields['username'].widget.attrs['class'] = 'input'
       self.fields['password'].widget.attrs['class'] = 'input'