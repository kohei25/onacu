import datetime

from django.contrib.auth.models import AbstractUser,UserManager
from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import gettext_lazy as _

# for validators=[MinValueValidator(), MaxValueValidator()] @ IntegerField
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"


# event model
class Event(models.Model):
    name = models.CharField(
        "イベント名", max_length=100, help_text="この項目は必須です。100文字以内にしてください。例: ○田□花 握手会",
    )
    host = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField("開催日時", help_text="この項目は必須です。",)
    # 1人あたりのビデオチャット時間，5s - 300s(5min)
    MIN_PERSONAL_TIME = 5
    MAX_PERSONAL_TIME = 300
    personal_time = models.IntegerField(
        "1人あたりの時間（秒）",
        validators=[
            MinValueValidator(MIN_PERSONAL_TIME),
            MaxValueValidator(MAX_PERSONAL_TIME),
        ],
        help_text="この項目は必須です。"
        + str(MIN_PERSONAL_TIME)
        + "秒以上、"
        + str(MAX_PERSONAL_TIME)
        + "秒以下にしてください。",
    )
    # 1人あたり購入できるチケット数
    # person_max = models.IntegerField(default=1, validators=[MaxValueValidator(5)])
    # 購入されたチケットの数
    purchaced_ticket = models.IntegerField(default=0)
    # 120枚は,30s/回で60分の計算
    MIN_TOTAL_TICKET = 1
    MAX_TOTAL_TICKET = 120
    total_ticket = models.IntegerField(
        "チケット発行数",
        validators=[
            MinValueValidator(MIN_TOTAL_TICKET),
            MaxValueValidator(MAX_TOTAL_TICKET),
        ],
        help_text="この項目は必須です。"
        + str(MIN_TOTAL_TICKET)
        + "枚以上、"
        + str(MAX_TOTAL_TICKET)
        + "枚以下にしてください。",
    )
    # eventの状態を表す
    # 0: イベント前，1: イベント中, 2: イベント後
    status = models.IntegerField(default=0)
    # イベントの写真URL
    image = models.ImageField("イメージ画像", blank=True, null=True, help_text="この項目は任意です。",)

    @property
    def is_able_to_enter(self):
        """開催日時の10分前から入場可能"""
        return self.status <= 1 and self.date - timezone.timedelta(minutes=10) < make_aware(timezone.datetime.now())

    @property
    def remains_ticket(self):
        """チケットの残り枚数"""
        return self.total_ticket - self.purchaced_ticket

    def __str__(self):
        return self.name + "," + self.host.username + str(self.date)

class UserAd(object):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 0:youtube, 1:twitter, 2:instagram, 3:tiktok, 4:その他サイト
    content = models.IntegerField()
    url = models.CharField()

        


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    peerId = models.CharField(default="0", max_length=16)

    class Meta:
        unique_together = (
            ("event", "customer"), # チケットは1人1枚
            ("event", "order"), # 各イベントでorderはユニーク
        )

    def __str__(self):
        return (
            "event: "
            + self.event.name
            + ", customer: "
            + self.customer.username
            + ", peerId: "
            + self.peerId
        )


class Wallet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    wallet = models.IntegerField(default=0)

    def __str__(self):
        return "owner: " + self.owner.username + ", wallet: " + str(self.wallet)
