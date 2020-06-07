import logging
from datetime import timedelta
from django.conf import settings
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
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.core.signing import BadSignature, SignatureExpired, loads, dumps
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .models import User, Event, Ticket, Wallet
from .forms import LoginForm, UserCreateForm, PwChangeForm, PwResetForm, PwSetForm, EventForm, EventBuyForm

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


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = "cms/signup_complete.html"
    timeout_seconds = getattr(
        settings, "ACTIVATION_TIMEOUT_SECONDS", 60 * 60 * 24
    )  # デフォルトでは1日以内

    def get(self, request, **kwargs):
        """tokenが正しければ本登録."""
        token = kwargs.get("token")
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)

        # 期限切れ
        except SignatureExpired:
            return HttpResponseBadRequest()

        # tokenが間違っている
        except BadSignature:
            return HttpResponseBadRequest()

        # tokenは問題なし
        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoesNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 問題なければ本登録とする
                    user.is_active = True
                    user.save()
                    login(request, user)
                    return super().get(request, **kwargs)

        return HttpResponseBadRequest()


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
    events = Event.objects.all()
    hosting_events = Event.objects.filter(host_id=request.user.id).exclude(status=2)
    have_tickets = Ticket.objects.filter(customer_id=request.user.id)
    purchased_events = list(map(lambda x: x.event, have_tickets))
    return render(
        request,
        "cms/top.html",
        {
            "events": events,
            "purchased_events": purchased_events,
            "hosting_events": hosting_events,
        },
    )


class TopView(generic.ListView):
    template_name = "cms/top.html"
    context_object_name = "coming_event_list"

    def get_queryset(self):
        return Event.objects.filter(status=0)


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


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "cms/event_new.html"
    success_url = reverse_lazy("cms:top")

    def form_valid(self, form):
        event = form.save(commit=False)
        event.host = self.request.user
        event.save()
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
            return HttpResponseBadRequest()
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
END:VCALENDAR""".format(start,end,event.name, request.scheme, request.get_host(), event.pk)
    response = HttpResponse(content, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename=event{}.ics'.format(event.pk)
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
    event.status = 2
    event.save()
    return render(request, "cms/event_finish.html")


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
