import datetime

from django.contrib.auth.base_user import (
    AbstractBaseUser, BaseUserManager,
)
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.forms import ModelForm
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# for validators=[MinValueValidator(), MaxValueValidator()] @ IntegerField
from django.core.validators import MaxValueValidator, MinValueValidator

# User-related
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class AbstractUser(AbstractBaseUser, PermissionsMixin):

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    email = models.EmailField(_('email address'), unique=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


# event model
class Event(models.Model):
  name = models.CharField(max_length=100)
  host = models.ForeignKey('User', on_delete=models.CASCADE)
  date = models.DateTimeField('event date')
  # 1人あたりのビデオチャット時間，30s - 300s(5min)
  personal_time = models.IntegerField(validators=[MinValueValidator(10), MaxValueValidator(300)])
  # 1人あたり購入できるチケット数
  # person_max = models.IntegerField(default=1, validators=[MaxValueValidator(5)])
  # 購入されたチケットの数
  purchaced_ticket = models.IntegerField(default=0)
  # 120枚は,30s/回で60分の計算
  total_ticket = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(120)])
  # eventの状態を表す
  # 0: イベント前，1: イベント前, 2: イベント中，3:イベント後
  status = models.IntegerField(default=0)
  # 繋いでるチャットのチケット番号
  order = models.IntegerField(default=0)

  def __str__(self):
    return self.name + "," + self.host.username

class Ticket(models.Model):
  event = models.ForeignKey(Event, on_delete=models.CASCADE)
  customer = models.ForeignKey(User, on_delete=models.CASCADE)
  order = models.IntegerField(default=0)
  peerId = models.CharField(default="0", max_length=16)

  def __str__(self):
    return  "event: " + self.event.name + ", customer: " + self.customer.username + ", peerId: " + self.peerId