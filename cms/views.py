import logging
from datetime import date, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.http.response import JsonResponse, HttpResponse
import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .models import User, Event, Ticket, Wallet, UserAd
from .forms import LoginForm, UserCreateForm, PwChangeForm, PwResetForm, PwSetForm, EventForm, EventBuyForm, UserAdForm

UserModel = get_user_model()

# user model
class Login(LoginView):
    form_class = LoginForm
    template_name = "cms/login.html"


class Logout(LogoutView):
    pass


class UserCreate(CreateView):
    """ユーザーの仮登録"""

    form_class = UserCreateForm
    template_name = "cms/signup.html"
    success_url = reverse_lazy("cms:top")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # 仮登録時はis_active = False
        user.save()

        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            "protocol": self.request.scheme,
            "domain": domain,
            "token": dumps(user.pk),
            "user": user,
        }
        subject = render_to_string("cms/mail_template/create/subject.txt", context)
        message = render_to_string("cms/mail_template/create/message.txt", context)

        user.email_user(subject, message)
        return redirect("cms:signup_done")


class UserCreateDone(TemplateView):
    """ユーザーの仮登録完了"""
    template_name = "cms/signup_done.html"


class UserCreateComplete(TemplateView):
    """メール内URLアクセス後のユーザー本登録 https://narito.ninja/blog/detail/42/"""
    template_name = "cms/signup_complete.html"
    success_url = reverse_lazy('cms:top')
    timeout_seconds = getattr(
        settings, "ACTIVATION_TIMEOUT_SECONDS", 60 * 60 * 3
    )  # デフォルトでは3時間以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get("token")
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            raise Http404("Signature expired")

        # tokenが間違っている
        except BadSignature:
            raise Http404("Bad signature")

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                raise Http404("User does not exist")
        
        if not user.is_active:
            # 問題なければ本登録とする
            user.is_active = True
            user.save()
            login(request, user)
            return super().get(request, **kwargs)
        messages.warning(request, '本登録が既に完了しています。')
        return super().get(request, **kwargs)


# Ajax
def ticketGet(request):
    """ホストがAjaxでファンのPeerIdを取得するエンドポイント"""
    eventId = request.GET.get("eventId", None)
    orderId = request.GET.get("ticketOrder", None)
    ticket = get_object_or_404(Ticket, event_id=eventId, order=orderId)
    if ticket.event.host != request.user:
        return HttpResponse("You are not the host of the event.", status=403)
    data = {
        "userPeerId": ticket.peerId,
        "orderId": orderId,
        "username": ticket.customer.username,
    }
    return JsonResponse(data)


def ticketPost(request):
    """ファンがAjaxでTicketのPeerIdを設定するエンドポイント"""
    ticketId = request.GET.get("ticketId", None)
    ticket = get_object_or_404(Ticket, pk=ticketId)
    if ticket.customer_id != request.user.id:
        return HttpResponse("You do not have the ticket.", status=403)
    userPeerId = request.GET.get("userPeerId", None)
    ticket.peerId = userPeerId
    ticket.save()
    data = {}
    return JsonResponse(data)


# Topページ
def topView(request):
    events = list(Event.objects.filter(status=0).order_by('date'))+list(Event.objects.exclude(status=0).order_by('status', '-date')) # 開催前は日時の昇順，その他は降順
    hosting_events = Event.objects.filter(host_id=request.user.id).exclude(status=2).order_by('date') # 終了した開催イベントは含まない
    have_tickets = Ticket.objects.filter(customer_id=request.user.id)
    purchased_events = list(filter(lambda event: event.status != 2, map(lambda ticket: ticket.event, have_tickets))) # 終了した購入済みイベントは含まない
    purchased_events.sort(key=lambda event: event.date)
    print(events)
    return render(
        request,
        "cms/top.html",
        {
            "events": events,
            "purchased_events": purchased_events,
            "hosting_events": hosting_events,
        },
    )

@cache_page(60) # 1分間キャッシュ
def searchView(request, year, month, day):
    MIN_DATE = date(2020,6,1) # サイト開設日（event_search.html中にも記載あり）
    try:
        d = date(year,month,day)
    except ValueError:
        raise Http404("The date is invalid")
    if d < MIN_DATE:
        raise Http404("The date is invalid") # サイト開設日以前の検索は無効
    search_events = Event.objects.filter(date__year=year, date__month=month, date__day=day)
    return render(
      request,
      'cms/event_search.html',
      {
        "events": search_events,
        "date": d,
      },
    )

@login_required
def myPageView(request):
    hosted_events = Event.objects.filter(host_id=request.user.id).filter(status=2)
    hosting_events = Event.objects.filter(host_id=request.user.id).exclude(status=2)
    have_tickets = Ticket.objects.filter(customer_id=request.user.id)
    purchased_events = list(map(lambda x: x.event, have_tickets))
    past_events = list(hosted_events) + list(
        filter(lambda x: x.status == 2, purchased_events)
    )
    future_events = list(hosting_events) + list(
        filter(lambda x: x.status != 2, purchased_events)
    )
    past_events.sort(key=lambda x: x.date, reverse=True)  # 過去のイベントは降順でソート
    future_events.sort(key=lambda x: x.date)  # 今後のイベントは昇順でソート
    return render(
        request,
        "cms/mypage.html",
        {
            "past_events": past_events,
            "future_events": future_events,
            "purchased_events": purchased_events,
        },
    )

@login_required
def userAd(request):
    if request.method == 'POST':
        form = UserAdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            try:
                ad.validate_unique()
            except ValidationError:
                messages.warning(request, 'このリンクは既に設置されています。')
            else:
                ad.save()
                form = UserAdForm()
    else:
        form = UserAdForm()
    ads = list(UserAd.objects.filter(user_id=request.user.id))
    return render(
        request,
        "cms/advertisement_config.html",
        {"ads": ads, "form": form},
    )

@login_required
def userAdDelete(request):
    if request.method == 'POST':
        id = request.POST["id"]
        ad = get_object_or_404(UserAd, pk=id)
        if ad.user == request.user:
            ad.delete()
        else:
            return HttpResponse("You are not the owner of the ad.", status=403)
    return redirect("cms:user-ad")

class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = PwChangeForm
    success_url = reverse_lazy('cms:password_change_done')
    template_name = 'cms/password_change.html'


class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    """パスワード変更完了"""
    template_name = 'cms/password_change_done.html'


class PasswordReset(PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'cms/mail_template/password_reset/subject.txt'
    email_template_name = 'cms/mail_template/password_reset/message.txt'
    template_name = 'cms/password_reset_form.html'
    form_class = PwResetForm
    success_url = reverse_lazy('cms:password_reset_done')


class PasswordResetDone(PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'cms/password_reset_done.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = PwSetForm
    success_url = reverse_lazy('cms:password_reset_complete')
    template_name = 'cms/password_reset_confirm.html'


class PasswordResetComplete(PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'cms/password_reset_complete.html'


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "cms/event_new.html"
    success_url = reverse_lazy("cms:top")

    def form_valid(self, form):
        event = form.save(commit=False)
        event.host = self.request.user
        event.save()
        messages.success(self.request, f'イベント「{event.name}」を作成しました。')
        return super(EventCreateView, self).form_valid(form)


def eventDetail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    is_ticket = Ticket.objects.filter(event_id=event.id, customer_id=request.user.id)
    return render(
        request, "cms/event_detail.html", {"event": event, "is_ticket": is_ticket}
    )


@login_required
def eventBuyView(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    is_ticket = Ticket.objects.filter(event_id=event.id, customer_id=request.user.id)

    if request.method == "POST": # チケット購入処理
        if is_ticket or event.host == request.user: # 既に持っている or ホストはイベントチケットを買えない
            raise PermissionDenied
        userId = request.user.id
        order = event.purchaced_ticket + 1
        ticket = Ticket(customer_id=userId, event_id=event.id, order=order)
        ticket.save()
        event.purchaced_ticket += 1
        event.save()
        return redirect("cms:buy_after", event_id)
    return render(request, "cms/event_buy.html", {"event": event})



def ticketBuyAfter(request, event_id):
    return render(request, "cms/event_buy_after.html", {"event_id": event_id})


@cache_page(60 * 60 * 24)
def event_ical(request, pk):
    """イベントのカレンダーファイルを配信"""
    event = get_object_or_404(Event, pk=pk)
    start = event.date.strftime("%Y%m%dT%H%M%SZ")
    end = (event.date + timedelta(seconds=(event.personal_time*event.total_ticket))).strftime("%Y%m%dT%H%M%SZ")
    content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OnAcu///JP
BEGIN:VEVENT
DTSTART:{}
DTEND:{}
SUMMARY:{}
URL:{}://{}/event/{}/
END:VEVENT
END:VCALENDAR""".format(start,end,event.name, request.scheme, request.get_host(), event.id)
    response = HttpResponse(content, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=event{}.ics'.format(event.id)
    return response


@login_required
def event_now(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user == event.host:
        event.status = 1
        event.save()
        ticket = Ticket.objects.filter(event_id=event.id).last()
    else:
        ticket = Ticket.objects.get(customer=request.user, event_id=event.id)
    return render(request, "cms/event_now.html", {"event": event, "ticket": ticket})


@login_required
def event_finish(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if event.host == request.user:
        event.status = 2
        event.save()
        ads = list(UserAd.objects.filter(user_id=event.host_id))
    return render(request, "cms/event_finish.html", {"event": event, "ads": ads})


@login_required
def pointBuy(request):
    if request.method == "POST":
        userId = request.user.id
        personal_wallet = Wallet.objects.get_or_create(owner_id=userId)
        get_point = int(request.POST["point"])
        personal_wallet[0].wallet += get_point
        personal_wallet[0].save()
        return redirect("cms:top")
    return render(request, "cms/point_buy.html")
