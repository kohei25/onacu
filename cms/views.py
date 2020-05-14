import logging
from django.contrib.auth import get_user_model, login
from django.contrib.auth.views import (
    LoginView, LogoutView,
)
from django.http import HttpResponseRedirect
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

# Topページ
class TopView(generic.ListView):
  template_name = 'cms/top.html'
  context_object_name = 'coming_event_list'

  def get_queryset(self):
    print("####IP Address for debug-toolbar: " + self.request.META['REMOTE_ADDR'] + "###")
    return Event.objects.all()

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
    event.status +=1
    event.save()
  return render(request, 'cms/event_now.html', {'event': event})

#   def get_context_data(self, **)
# def buy(request, event_id):
#   event = get_object_or_404(Event, pk=event_id)
#   print("event: " + str(event))
#   try:
#     print("try: " + str(event))
#     ticket_purchased = event.ticket_set.get(pk=request.POST['ticket'])
#     print("ticket_purchaced: " + str(ticket_purchased))
#   except(KeyError, Ticket.DoesNotExist):
#     print("**************************************")
#     return render(request, 'cms/event_detail.html', {
#       'event': event,
#       'error_messege': "購入に失敗しました。",
#     })
#   else:
#     print("else: " + str(event))
#     event.total_ticket -= 1
#     ticket_purchased.event_id = event_id
#     ticket_purchased.customer = self.request.user
#     ticket_purchased.save()
#     print("return: " + str(event))
#   # finally:
#   #   return HttpResponseRedirect(reverse('cms:top'))




  # def get_queryset(set):
  #   return Event.objects()