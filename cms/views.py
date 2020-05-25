import logging
import ipdb
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import (
    LoginView, LogoutView,
)
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.views.generic import TemplateView
# from django.views.generic import CreateView
from django.views.generic.edit import CreateView

from .models import Event, Ticket
from .forms import LoginForm, UserCreateForm, EventForm, EventBuyForm


UserModel = get_user_model()

# user model
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

# Ajax
def ticketGet(request):
  eventId = request.GET.get('eventId', None);
  orderId = request.GET.get('ticketOrder', None);
  # ipdb.set_trace()
  data = {
    'userPeerId': Ticket.objects.get(event_id = eventId, order = orderId).peerId,
    'orderId': orderId,
  }
  return JsonResponse(data)

def ticketPost(request):
  userPeerId = request.GET.get('userPeerId', None);
  ticketId = request.GET.get('ticketId', None);
  # ipdb.set_trace()
  set_ticket = Ticket.objects.get(pk=ticketId)
  set_ticket.peerId = userPeerId
  set_ticket.save()
  # ipdb.set_trace()
  data = {
    'status': 'success_ajax',
  }
  return JsonResponse(data)

# Topページ
def topView(request):
  events = Event.objects.all()
  return render(request, 'cms/top.html', {'events': events})



class TopView(generic.ListView):
  template_name = 'cms/top.html'
  context_object_name = 'coming_event_list'

  def get_queryset(self):
    return Event.objects.filter(status=0)

class Top1View(generic.ListView):
  template_name = 'cms/top1.html'
  context_object_name = 'coming_event_list'

  def get_queryset(self):
    # print("####IP Address for debug-toolbar: " + self.request.META['REMOTE_ADDR'] + "###")
    box = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    return box


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'cms/event_new.html'
    success_url = reverse_lazy('cms:top')

    def form_valid(self, form):
      event = form.save(commit=False)
      event.host = self.request.user
      event.save()
      return super(EventCreateView, self).form_valid(form)

class EventDetailView(generic.DetailView):
  model = Event
  template_name = 'cms/event_detail.html'


class EventBuyView(CreateView):
  model = Ticket
  form_class = EventBuyForm
  template_name = 'cms/event_buy.html'
  # Event詳細画面にアクセスする
  success_url = reverse_lazy('cms:top')

  def form_valid(self, form):
    ticket = form.save(commit=False)
    event = ticket.event
    ticket.order = event.purchaced_ticket + 1
    # print(ticket.order)
    print(event.purchaced_ticket)
    event.purchaced_ticket += 1
    event.save()
    print(event.purchaced_ticket)
    ticket.customer = self.request.user
    ticket.save()
    return super(EventBuyView, self).form_valid(form)


def event_now(request, pk):
  event = get_object_or_404(Event, pk=pk)
  if request.user == event.host:
    event.status = 1
    event.save()
    ticket = Ticket.objects.filter(event_id=event.id).last()
  else:
    ticket = Ticket.objects.get(customer=request.user, event_id=event.id)
    # ipdb.set_trace()
  return render(request, 'cms/event_now.html', {'event': event, 'ticket': ticket})

def event_finish(request, pk):
  event = get_object_or_404(Event, pk=pk)
  event.status = 2
  event.save()
  return render(request, 'cms/event_finish.html')